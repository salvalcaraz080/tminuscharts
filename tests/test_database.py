import sqlite3
from unittest.mock import patch

import pytest
import database


# ---------------------------------------------------------------------------
# init_db
# ---------------------------------------------------------------------------

class TestInitDb:
    def test_creates_all_tables(self, tmp_path):
        db_file = tmp_path / "test.db"
        with patch.object(database, "DB_PATH", db_file):
            database.init_db()

        conn = sqlite3.connect(db_file)
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        conn.close()

        assert {"launches", "rockets", "pads", "launch_service_providers"}.issubset(tables)

    def test_creates_indexes(self, tmp_path):
        db_file = tmp_path / "test.db"
        with patch.object(database, "DB_PATH", db_file):
            database.init_db()

        conn = sqlite3.connect(db_file)
        indexes = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index'"
        ).fetchall()}
        conn.close()

        assert "idx_launches_net" in indexes
        assert "idx_launches_status" in indexes

    def test_migration_adds_missing_columns(self, tmp_path):
        db_file = tmp_path / "test.db"

        # Create old-style schema without logo_url / image_url
        conn = sqlite3.connect(db_file)
        conn.executescript("""
            CREATE TABLE launch_service_providers (
                id INTEGER PRIMARY KEY, name TEXT NOT NULL,
                country TEXT, type TEXT,
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE rockets (
                id INTEGER PRIMARY KEY, name TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE pads (id INTEGER PRIMARY KEY, name TEXT NOT NULL, location TEXT, country TEXT, latitude REAL, longitude REAL);
            CREATE TABLE launches (id TEXT PRIMARY KEY, name TEXT NOT NULL, net TEXT, status_name TEXT, rocket_id INTEGER, provider_id INTEGER, pad_id INTEGER);
        """)
        conn.commit()
        conn.close()

        with patch.object(database, "DB_PATH", db_file):
            database.init_db()

        conn = sqlite3.connect(db_file)
        lsp_cols = {r[1] for r in conn.execute("PRAGMA table_info(launch_service_providers)").fetchall()}
        rocket_cols = {r[1] for r in conn.execute("PRAGMA table_info(rockets)").fetchall()}
        conn.close()

        assert "logo_url" in lsp_cols
        assert "image_url" in lsp_cols
        assert "image_url" in rocket_cols

    def test_idempotent_when_run_twice(self, tmp_path):
        db_file = tmp_path / "test.db"
        with patch.object(database, "DB_PATH", db_file):
            database.init_db()
            database.init_db()  # should not raise


# ---------------------------------------------------------------------------
# upsert_provider
# ---------------------------------------------------------------------------

class TestUpsertProvider:
    def test_none_returns_none(self, mem_conn):
        assert database.upsert_provider(mem_conn, None) is None

    def test_inserts_new_provider(self, mem_conn):
        provider = {"id": 1, "name": "SpaceX", "country_code": "USA",
                    "type": "Commercial", "logo_url": None, "image_url": None}
        returned_id = database.upsert_provider(mem_conn, provider)
        mem_conn.commit()

        assert returned_id == 1
        row = mem_conn.execute(
            "SELECT * FROM launch_service_providers WHERE id=1"
        ).fetchone()
        assert row["name"] == "SpaceX"
        assert row["country"] == "USA"

    def test_updates_existing_provider(self, mem_conn):
        provider = {"id": 1, "name": "SpaceX", "country_code": "USA",
                    "type": "Commercial", "logo_url": None, "image_url": None}
        database.upsert_provider(mem_conn, provider)

        updated = {**provider, "name": "SpaceX Inc.", "logo_url": "https://logo.png"}
        database.upsert_provider(mem_conn, updated)
        mem_conn.commit()

        row = mem_conn.execute(
            "SELECT * FROM launch_service_providers WHERE id=1"
        ).fetchone()
        assert row["name"] == "SpaceX Inc."
        assert row["logo_url"] == "https://logo.png"

    def test_logo_url_coalesce_preserves_existing(self, mem_conn):
        """Updating with logo_url=None should not overwrite an existing URL."""
        provider = {"id": 1, "name": "SpaceX", "country_code": "USA",
                    "type": "Commercial", "logo_url": "https://logo.png", "image_url": None}
        database.upsert_provider(mem_conn, provider)

        no_logo = {**provider, "logo_url": None}
        database.upsert_provider(mem_conn, no_logo)
        mem_conn.commit()

        row = mem_conn.execute(
            "SELECT logo_url FROM launch_service_providers WHERE id=1"
        ).fetchone()
        assert row["logo_url"] == "https://logo.png"


# ---------------------------------------------------------------------------
# upsert_rocket
# ---------------------------------------------------------------------------

class TestUpsertRocket:
    def test_none_returns_none(self, mem_conn):
        assert database.upsert_rocket(mem_conn, None) is None

    def test_inserts_new_rocket(self, mem_conn):
        config = {"id": 164, "name": "Falcon 9", "family": "Falcon",
                  "variant": "Block 5", "full_name": "Falcon 9 Block 5", "image_url": None}
        database.upsert_rocket(mem_conn, config)
        mem_conn.commit()

        row = mem_conn.execute("SELECT * FROM rockets WHERE id=164").fetchone()
        assert row["name"] == "Falcon 9"
        assert row["family"] == "Falcon"

    def test_updates_existing_rocket(self, mem_conn):
        config = {"id": 164, "name": "Falcon 9", "family": "Falcon",
                  "variant": "Block 5", "full_name": "Falcon 9 Block 5", "image_url": None}
        database.upsert_rocket(mem_conn, config)

        updated = {**config, "variant": "Block 5 v2"}
        database.upsert_rocket(mem_conn, updated)
        mem_conn.commit()

        row = mem_conn.execute("SELECT variant FROM rockets WHERE id=164").fetchone()
        assert row["variant"] == "Block 5 v2"

    def test_image_url_coalesce_preserves_existing(self, mem_conn):
        config = {"id": 164, "name": "Falcon 9", "family": "Falcon",
                  "variant": "Block 5", "full_name": "Falcon 9 Block 5",
                  "image_url": "https://img.png"}
        database.upsert_rocket(mem_conn, config)

        database.upsert_rocket(mem_conn, {**config, "image_url": None})
        mem_conn.commit()

        row = mem_conn.execute("SELECT image_url FROM rockets WHERE id=164").fetchone()
        assert row["image_url"] == "https://img.png"


# ---------------------------------------------------------------------------
# upsert_pad
# ---------------------------------------------------------------------------

class TestUpsertPad:
    def test_none_returns_none(self, mem_conn):
        assert database.upsert_pad(mem_conn, None) is None

    def test_inserts_new_pad(self, mem_conn):
        pad = {
            "id": 87, "name": "LC-39A",
            "location": {"name": "Kennedy Space Center, FL", "country_code": "USA"},
            "latitude": 28.608, "longitude": -80.604,
        }
        database.upsert_pad(mem_conn, pad)
        mem_conn.commit()

        row = mem_conn.execute("SELECT * FROM pads WHERE id=87").fetchone()
        assert row["name"] == "LC-39A"
        assert row["country"] == "USA"
        assert row["latitude"] == pytest.approx(28.608)

    def test_updates_existing_pad(self, mem_conn):
        pad = {
            "id": 87, "name": "LC-39A",
            "location": {"name": "Kennedy", "country_code": "USA"},
            "latitude": 28.0, "longitude": -80.0,
        }
        database.upsert_pad(mem_conn, pad)
        database.upsert_pad(mem_conn, {**pad, "latitude": 28.608})
        mem_conn.commit()

        row = mem_conn.execute("SELECT latitude FROM pads WHERE id=87").fetchone()
        assert row["latitude"] == pytest.approx(28.608)

    def test_pad_without_location_dict(self, mem_conn):
        pad = {"id": 99, "name": "Unknown Pad", "latitude": None, "longitude": None}
        database.upsert_pad(mem_conn, pad)
        mem_conn.commit()

        row = mem_conn.execute("SELECT country FROM pads WHERE id=99").fetchone()
        assert row["country"] is None


# ---------------------------------------------------------------------------
# upsert_launch (integration: calls all upsert_* helpers internally)
# ---------------------------------------------------------------------------

SAMPLE_LAUNCH = {
    "id": "abc-123-uuid",
    "name": "Falcon 9 | Starlink Group 4-1",
    "slug": "falcon-9-starlink-group-4-1",
    "status": {"id": 3, "name": "Launch Successful"},
    "net": "2022-03-15T08:00:00Z",
    "window_start": "2022-03-15T07:00:00Z",
    "window_end": "2022-03-15T09:00:00Z",
    "mission": {
        "name": "Starlink Group 4-1",
        "type": "Communications",
        "orbit": {"name": "Low Earth Orbit"},
        "description": "Batch of Starlink satellites.",
    },
    "rocket": {
        "configuration": {
            "id": 164, "name": "Falcon 9", "family": "Falcon",
            "variant": "Block 5", "full_name": "Falcon 9 Block 5", "image_url": None,
        }
    },
    "launch_service_provider": {
        "id": 121, "name": "SpaceX", "country_code": "USA",
        "type": "Commercial", "logo_url": None, "image_url": None,
    },
    "pad": {
        "id": 87, "name": "LC-39A",
        "location": {"name": "Kennedy Space Center, FL", "country_code": "USA"},
        "latitude": 28.608, "longitude": -80.604,
    },
    "image": "https://example.com/launch.jpg",
}


class TestUpsertLaunch:
    def test_inserts_launch_and_related_entities(self, mem_conn):
        database.upsert_launch(mem_conn, SAMPLE_LAUNCH)
        mem_conn.commit()

        row = mem_conn.execute(
            "SELECT * FROM launches WHERE id='abc-123-uuid'"
        ).fetchone()
        assert row is not None
        assert row["name"] == "Falcon 9 | Starlink Group 4-1"
        assert row["status_name"] == "Launch Successful"
        assert row["mission_orbit"] == "Low Earth Orbit"

    def test_related_entities_created(self, mem_conn):
        database.upsert_launch(mem_conn, SAMPLE_LAUNCH)
        mem_conn.commit()

        assert mem_conn.execute("SELECT id FROM rockets WHERE id=164").fetchone() is not None
        assert mem_conn.execute(
            "SELECT id FROM launch_service_providers WHERE id=121"
        ).fetchone() is not None
        assert mem_conn.execute("SELECT id FROM pads WHERE id=87").fetchone() is not None

    def test_updates_on_second_upsert(self, mem_conn):
        database.upsert_launch(mem_conn, SAMPLE_LAUNCH)
        updated = {**SAMPLE_LAUNCH, "status": {"id": 4, "name": "Launch Failure"}}
        database.upsert_launch(mem_conn, updated)
        mem_conn.commit()

        row = mem_conn.execute(
            "SELECT status_name FROM launches WHERE id='abc-123-uuid'"
        ).fetchone()
        assert row["status_name"] == "Launch Failure"

    def test_launch_with_missing_optional_fields(self, mem_conn):
        minimal = {
            "id": "minimal-uuid",
            "name": "Unknown Launch",
            "rocket": {},
            "launch_service_provider": {},
            "pad": {},
            "mission": {},
            "status": {},
        }
        database.upsert_launch(mem_conn, minimal)
        mem_conn.commit()

        row = mem_conn.execute(
            "SELECT * FROM launches WHERE id='minimal-uuid'"
        ).fetchone()
        assert row is not None
        assert row["mission_orbit"] is None
        assert row["rocket_id"] is None
