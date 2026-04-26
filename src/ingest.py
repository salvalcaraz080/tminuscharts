"""
T-Minus Data — Ingestion script for Launch Library 2 API.

Pulls launch data (past and upcoming) and stores it in SQLite.

API docs: https://ll.thespacedevs.com/2.2.0/swagger/

Endpoints:
- Production (ll.thespacedevs.com): 15 requests/hour, full historical data
- Development (lldev.thespacedevs.com): no rate limit, ~500 launch sample, stale

Usage:
    # Quick test with dev API (limited dataset):
    python src/ingest.py --dev

    # Full historical ingest (takes ~5 hours due to rate limits):
    python src/ingest.py --full-history

    # Only recent launches (faster):
    python src/ingest.py --full-history --since-year 2015
"""

import argparse
import time
from datetime import datetime

import requests

from database import get_connection, init_db, upsert_launch

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PROD_BASE = "https://ll.thespacedevs.com/2.2.0"
DEV_BASE = "https://lldev.thespacedevs.com/2.2.0"
PAGE_SIZE = 100

# Production rate limit: 15 requests/hour → one every 240s.
# We wait 260s to stay safely under.
PROD_DELAY = 260
DEV_DELAY = 1


def fetch_page(base_url: str, endpoint: str, offset: int, extra_params: dict, min_wait: int = 0) -> dict:
    """Fetch a single page from the API with retry logic."""
    url = f"{base_url}/{endpoint}/"
    params = {"limit": PAGE_SIZE, "offset": offset, "mode": "detailed", **extra_params}

    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=30)

            if resp.status_code == 429:
                # Retry-After from the server is often unreliable (e.g. 2s when the
                # actual hourly window won't reset for minutes). Enforce at least min_wait.
                retry_after = max(int(resp.headers.get("Retry-After", 3600)), min_wait)
                print(f"  ⏳ Rate limited. Waiting {retry_after}s...")
                time.sleep(retry_after)
                continue

            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            wait = 30 * (attempt + 1)
            print(f"  ⚠️  Request error: {e}. Retrying in {wait}s...")
            time.sleep(wait)

    print("  ❌ Failed after 3 attempts. Skipping page.")
    return {"results": [], "next": None, "count": 0}


def ingest_launches(
    base_url: str,
    endpoint: str,
    delay: int,
    max_pages: int | None = None,
    extra_params: dict | None = None,
) -> int:
    """Paginate through an API endpoint and store all launches."""
    conn = get_connection()
    extra_params = extra_params or {}
    offset = 0
    total = 0
    page = 0

    data = fetch_page(base_url, endpoint, offset, extra_params, min_wait=delay)
    count = data.get("count", 0)
    print(f"📡 Found {count} launches in /{endpoint}/")

    while True:
        results = data.get("results", [])
        if not results:
            break

        for launch in results:
            upsert_launch(conn, launch)
            total += 1

        conn.commit()
        page += 1

        # ETA estimate
        remaining_pages = (count - total + PAGE_SIZE - 1) // PAGE_SIZE
        eta_min = remaining_pages * delay // 60
        print(
            f"  ✅ Page {page}: stored {len(results)} launches "
            f"({total}/{count} total) — ETA ~{eta_min} min"
        )

        if max_pages and page >= max_pages:
            print(f"  🛑 Reached max pages ({max_pages}). Stopping.")
            break

        if not data.get("next"):
            break

        time.sleep(delay)
        offset += PAGE_SIZE
        data = fetch_page(base_url, endpoint, offset, extra_params, min_wait=delay)

    conn.close()
    return total


def main():
    parser = argparse.ArgumentParser(description="T-Minus Data — Launch ingestion")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Use dev API endpoint (no rate limits, limited stale data ~500 launches)",
    )
    parser.add_argument(
        "--full-history",
        action="store_true",
        help="Ingest ALL historical launches (slow with prod API, ~5 hours)",
    )
    parser.add_argument(
        "--since-year",
        type=int,
        default=None,
        help="Only fetch launches from this year onwards (e.g. 2015)",
    )
    args = parser.parse_args()

    base_url = DEV_BASE if args.dev else PROD_BASE
    delay = DEV_DELAY if args.dev else PROD_DELAY

    mode_label = "FULL HISTORY" if args.full_history else "QUICK (1 page)"

    print("🚀 T-Minus Data — Launch Ingestion")
    print(f"   Mode: {mode_label}")
    print(f"   Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Endpoint: {base_url}")
    print(f"   Delay between requests: {delay}s")
    if args.since_year:
        print(f"   Filter: launches from {args.since_year}-01-01 onwards")
    print()

    init_db()

    # Build filter for since_year
    extra_params = {}
    if args.since_year:
        extra_params["net__gte"] = f"{args.since_year}-01-01T00:00:00Z"

    # 1. Upcoming launches
    print("─" * 50)
    print("UPCOMING LAUNCHES")
    print("─" * 50)
    upcoming = ingest_launches(base_url, "launch/upcoming", delay, max_pages=None)

    # 2. Past launches
    print()
    print("─" * 50)
    print("PAST LAUNCHES")
    print("─" * 50)
    max_pages = None if args.full_history else 1
    past = ingest_launches(
        base_url, "launch/previous", delay,
        max_pages=max_pages, extra_params=extra_params,
    )

    # Summary
    conn = get_connection()
    total_in_db = conn.execute("SELECT COUNT(*) FROM launches").fetchone()[0]
    conn.close()

    print()
    print("═" * 50)
    print(f"✅ Done! Ingested {upcoming + past} launches in this run.")
    print(f"   Upcoming: {upcoming}")
    print(f"   Past:     {past}")
    print(f"   Total in database: {total_in_db}")
    print(f"   Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 50)


if __name__ == "__main__":
    main()