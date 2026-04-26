"""
T-Minus Charts — SQLite database setup and operations.

Stores launch data from Launch Library 2 API in a local SQLite database.
Designed for easy migration to PostgreSQL/Supabase when needed.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "tminuscharts.db"


def get_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create tables if they don't exist and run lightweight migrations."""
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS launch_service_providers (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            country     TEXT,
            type        TEXT,
            logo_url    TEXT,
            image_url   TEXT,
            updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS rockets (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            family      TEXT,
            variant     TEXT,
            full_name   TEXT,
            image_url   TEXT,
            updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS pads (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            location    TEXT,
            country     TEXT,
            latitude    REAL,
            longitude   REAL,
            updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS launches (
            id              TEXT PRIMARY KEY,   -- UUID from API
            name            TEXT NOT NULL,
            slug            TEXT,
            status_id       INTEGER,
            status_name     TEXT,
            net             TEXT,               -- No Earlier Than (datetime)
            window_start    TEXT,
            window_end      TEXT,
            mission_name    TEXT,
            mission_type    TEXT,
            mission_orbit   TEXT,
            mission_description TEXT,
            rocket_id       INTEGER REFERENCES rockets(id),
            provider_id     INTEGER REFERENCES launch_service_providers(id),
            pad_id          INTEGER REFERENCES pads(id),
            image_url       TEXT,
            updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_launches_net ON launches(net);
        CREATE INDEX IF NOT EXISTS idx_launches_status ON launches(status_name);
        CREATE INDEX IF NOT EXISTS idx_launches_provider ON launches(provider_id);

        CREATE TABLE IF NOT EXISTS tweeted_launches (
            launch_id  TEXT PRIMARY KEY,
            tweeted_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
    )

    # Lightweight migrations for databases created before image columns existed.
    def _has_column(table: str, col: str) -> bool:
        cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
        return any(c["name"] == col for c in cols)

    if not _has_column("launch_service_providers", "logo_url"):
        conn.execute("ALTER TABLE launch_service_providers ADD COLUMN logo_url TEXT")
    if not _has_column("launch_service_providers", "image_url"):
        conn.execute("ALTER TABLE launch_service_providers ADD COLUMN image_url TEXT")
    if not _has_column("rockets", "image_url"):
        conn.execute("ALTER TABLE rockets ADD COLUMN image_url TEXT")

    conn.commit()
    conn.close()


def upsert_provider(conn: sqlite3.Connection, provider: dict) -> int | None:
    """Insert or update a launch service provider. Returns provider id."""
    if not provider:
        return None
    conn.execute(
        """
        INSERT INTO launch_service_providers
            (id, name, country, type, logo_url, image_url)
        VALUES (:id, :name, :country, :type, :logo_url, :image_url)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name, country=excluded.country,
            type=excluded.type,
            logo_url=COALESCE(excluded.logo_url, launch_service_providers.logo_url),
            image_url=COALESCE(excluded.image_url, launch_service_providers.image_url),
            updated_at=datetime('now')
        """,
        {
            "id": provider.get("id"),
            "name": provider.get("name", "Unknown"),
            "country": provider.get("country_code"),
            "type": provider.get("type"),
            "logo_url": provider.get("logo_url"),
            "image_url": provider.get("image_url"),
        },
    )
    return provider.get("id")


def upsert_rocket(conn: sqlite3.Connection, rocket_config: dict) -> int | None:
    """Insert or update a rocket configuration. Returns rocket id."""
    if not rocket_config:
        return None
    conn.execute(
        """
        INSERT INTO rockets (id, name, family, variant, full_name, image_url)
        VALUES (:id, :name, :family, :variant, :full_name, :image_url)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name, family=excluded.family,
            variant=excluded.variant, full_name=excluded.full_name,
            image_url=COALESCE(excluded.image_url, rockets.image_url),
            updated_at=datetime('now')
        """,
        {
            "id": rocket_config.get("id"),
            "name": rocket_config.get("name", "Unknown"),
            "family": rocket_config.get("family"),
            "variant": rocket_config.get("variant"),
            "full_name": rocket_config.get("full_name"),
            "image_url": rocket_config.get("image_url"),
        },
    )
    return rocket_config.get("id")


def upsert_pad(conn: sqlite3.Connection, pad: dict) -> int | None:
    """Insert or update a launch pad. Returns pad id."""
    if not pad:
        return None
    location = pad.get("location") or {}
    conn.execute(
        """
        INSERT INTO pads (id, name, location, country, latitude, longitude)
        VALUES (:id, :name, :location, :country, :latitude, :longitude)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name, location=excluded.location,
            country=excluded.country, latitude=excluded.latitude,
            longitude=excluded.longitude, updated_at=datetime('now')
        """,
        {
            "id": pad.get("id"),
            "name": pad.get("name", "Unknown"),
            "location": location.get("name"),
            "country": location.get("country_code"),
            "latitude": pad.get("latitude"),
            "longitude": pad.get("longitude"),
        },
    )
    return pad.get("id")


def upsert_launch(conn: sqlite3.Connection, launch: dict) -> None:
    """Insert or update a launch record, including related entities."""
    rocket = launch.get("rocket") or {}
    rocket_config = rocket.get("configuration") or {}
    provider = launch.get("launch_service_provider") or {}
    pad = launch.get("pad") or {}
    mission = launch.get("mission") or {}
    status = launch.get("status") or {}

    provider_id = upsert_provider(conn, provider)
    rocket_id = upsert_rocket(conn, rocket_config)
    pad_id = upsert_pad(conn, pad)

    conn.execute(
        """
        INSERT INTO launches (
            id, name, slug, status_id, status_name,
            net, window_start, window_end,
            mission_name, mission_type, mission_orbit, mission_description,
            rocket_id, provider_id, pad_id, image_url
        ) VALUES (
            :id, :name, :slug, :status_id, :status_name,
            :net, :window_start, :window_end,
            :mission_name, :mission_type, :mission_orbit, :mission_description,
            :rocket_id, :provider_id, :pad_id, :image_url
        )
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name, slug=excluded.slug,
            status_id=excluded.status_id, status_name=excluded.status_name,
            net=excluded.net, window_start=excluded.window_start,
            window_end=excluded.window_end,
            mission_name=excluded.mission_name, mission_type=excluded.mission_type,
            mission_orbit=excluded.mission_orbit,
            mission_description=excluded.mission_description,
            rocket_id=excluded.rocket_id, provider_id=excluded.provider_id,
            pad_id=excluded.pad_id, image_url=excluded.image_url,
            updated_at=datetime('now')
        """,
        {
            "id": launch.get("id"),
            "name": launch.get("name", "Unknown"),
            "slug": launch.get("slug"),
            "status_id": status.get("id"),
            "status_name": status.get("name"),
            "net": launch.get("net"),
            "window_start": launch.get("window_start"),
            "window_end": launch.get("window_end"),
            "mission_name": mission.get("name"),
            "mission_type": mission.get("type"),
            "mission_orbit": (mission.get("orbit") or {}).get("name"),
            "mission_description": mission.get("description"),
            "rocket_id": rocket_id,
            "provider_id": provider_id,
            "pad_id": pad_id,
            "image_url": launch.get("image"),
        },
    )
