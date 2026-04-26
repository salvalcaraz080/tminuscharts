import sys
from pathlib import Path
from unittest.mock import MagicMock

# Mock streamlit before any dashboard module is imported at collection time
_st_mock = MagicMock()
_st_mock.cache_data = lambda **kwargs: (lambda f: f)
sys.modules["streamlit"] = _st_mock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "dashboard"))

import sqlite3
import pytest
import pandas as pd


@pytest.fixture
def sample_past():
    """Seven past launches across 2022-2023 covering all insight scenarios."""
    return pd.DataFrame({
        "year": [2022, 2022, 2022, 2023, 2023, 2023, 2023],
        "provider_name": ["SpaceX", "SpaceX", "Rocket Lab", "SpaceX", "SpaceX", "ISRO", "SpaceX"],
        "provider_country": ["USA", "USA", "NZL", "USA", "USA", "IND", "USA"],
        "provider_type": ["Commercial", "Commercial", "Commercial", "Commercial", "Commercial", "Government", "Commercial"],
        "net": pd.to_datetime([
            "2022-03-15", "2022-06-20", "2022-09-10",
            "2023-01-10", "2023-03-15", "2023-06-20", "2023-10-05",
        ], utc=True),
        "pad_name": ["LC-39A", "SLC-40", "LC-1", "LC-39A", "SLC-40", "SDSC", "LC-39A"],
        "pad_location": ["Kennedy", "Kennedy", "Mahia", "Kennedy", "Kennedy", "Sriharikota", "Kennedy"],
        "pad_country": ["USA", "USA", "NZL", "USA", "USA", "IND", "USA"],
        "mission_orbit": [
            "Low Earth Orbit", "Low Earth Orbit", "Lunar Orbit",
            "Low Earth Orbit", "Geostationary Transfer Orbit",
            "Sun-Synchronous Orbit", "Low Earth Orbit",
        ],
        "mission_name": [
            "Starlink Group 4-1", "Transporter-6", "CAPSTONE",
            "Starlink Group 5-1", "SES-18", "PSLV-C55", "Starlink Group 6-1",
        ],
        "launch_name": [
            "Starlink Group 4-1", "Transporter-6", "CAPSTONE Lunar Mission",
            "Starlink Group 5-1", "SES-18 & SES-19", "PSLV-C55", "Starlink Group 6-1",
        ],
        "mission_type": [
            "Communications", "Technology", "Planetary Science",
            "Communications", "Communications", "Earth Science", "Communications",
        ],
        "rocket_name": [
            "Falcon 9", "Falcon 9", "Electron",
            "Falcon 9", "Falcon 9", "PSLV", "Falcon 9",
        ],
        "status_name": [
            "Launch Successful", "Launch Successful", "Launch Successful",
            "Launch Successful", "Launch Successful", "Launch Successful", "Launch Failure",
        ],
        "provider_logo_url": [None] * 7,
    })


@pytest.fixture
def sample_upcoming():
    """Three upcoming launches across two ISO weeks."""
    return pd.DataFrame({
        "net": pd.to_datetime([
            "2025-01-06 10:00",  # Monday – week 1
            "2025-01-07 12:00",  # Tuesday – week 1
            "2025-01-13 09:00",  # Monday – week 2
        ], utc=True),
        "launch_name": ["Mission A", "Mission B", "Mission C"],
        "provider_name": ["SpaceX", "Rocket Lab", "SpaceX"],
    })


@pytest.fixture
def mem_conn():
    """In-memory SQLite connection with the full production schema."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript("""
        CREATE TABLE launch_service_providers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            country TEXT, type TEXT, logo_url TEXT, image_url TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE rockets (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL, family TEXT, variant TEXT,
            full_name TEXT, image_url TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE pads (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL, location TEXT, country TEXT,
            latitude REAL, longitude REAL,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE launches (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, slug TEXT,
            status_id INTEGER, status_name TEXT,
            net TEXT, window_start TEXT, window_end TEXT,
            mission_name TEXT, mission_type TEXT, mission_orbit TEXT,
            mission_description TEXT,
            rocket_id INTEGER REFERENCES rockets(id),
            provider_id INTEGER REFERENCES launch_service_providers(id),
            pad_id INTEGER REFERENCES pads(id),
            image_url TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)
    yield conn
    conn.close()
