"""Cached data loaders for the T-Minus Charts dashboard."""

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).parent.parent / "data" / "tminuscharts.db"


def _connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


@st.cache_data(ttl=600)
def load_launches() -> pd.DataFrame:
    """Load all launches joined with rockets, providers and pads."""
    if not DB_PATH.exists():
        return pd.DataFrame()

    query = """
        SELECT
            l.id, l.name AS launch_name, l.slug,
            l.status_name,
            l.net, l.window_start, l.window_end,
            l.mission_name, l.mission_type, l.mission_orbit, l.mission_description,
            l.image_url AS launch_image_url,
            r.name     AS rocket_name,
            r.family   AS rocket_family,
            r.full_name AS rocket_fullname,
            r.image_url AS rocket_image_url,
            p.name    AS provider_name,
            p.country AS provider_country,
            p.type    AS provider_type,
            p.logo_url  AS provider_logo_url,
            p.image_url AS provider_image_url,
            pad.name      AS pad_name,
            pad.location  AS pad_location,
            pad.country   AS pad_country,
            pad.latitude, pad.longitude
        FROM launches l
        LEFT JOIN rockets   r   ON l.rocket_id   = r.id
        LEFT JOIN launch_service_providers p ON l.provider_id = p.id
        LEFT JOIN pads      pad ON l.pad_id      = pad.id
    """
    conn = _connect()
    df = pd.read_sql(query, conn)
    conn.close()

    # Parse datetimes (API returns ISO 8601 UTC)
    for col in ("net", "window_start", "window_end"):
        df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)

    df["year"]  = df["net"].dt.year
    df["month"] = df["net"].dt.to_period("M").astype(str)

    return df


def split_past_upcoming(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split launches into past (already happened) and upcoming."""
    now = pd.Timestamp.now(tz="UTC")
    past = df[df["net"] < now].copy()
    upcoming = df[df["net"] >= now].copy().sort_values("net")
    return past, upcoming


def success_rate(past: pd.DataFrame) -> float:
    """Compute launch success rate from past launches."""
    if past.empty:
        return 0.0
    success_statuses = {"Launch Successful", "Success"}
    successes = past["status_name"].isin(success_statuses).sum()
    total_concluded = past["status_name"].isin(
        success_statuses | {"Launch Failure", "Failure", "Partial Failure"}
    ).sum()
    return (successes / total_concluded * 100) if total_concluded else 0.0
