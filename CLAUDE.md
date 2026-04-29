# T-Minus Charts · Claude Instructions

Space launch analytics dashboard. Data from Launch Library 2 API → SQLite → Streamlit dashboard with Plotly charts. Deployed on Streamlit Community Cloud.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Dashboard | Streamlit |
| Charts | Plotly |
| Database | SQLite (committed to repo) |
| Data API | Launch Library 2 |
| Hosting | Streamlit Community Cloud |

---

## Key files

```
src/
  ingest.py       API ingestion script (fetch → upsert → SQLite)
  database.py     Schema, migrations, upsert_* functions

dashboard/
  app.py          Streamlit UI — layout and widget calls only
  data.py         Cached SQL loaders (load_launches, load_providers, split_past_upcoming, success_rate)
  insights.py     Pure analytics functions — no Streamlit imports
  i18n.py         Flat bilingual dict {key: {EN: ..., ES: ...}}
  theme.py        CSS injection, mc_fig(), Plotly theme

tests/
  conftest.py     Shared fixtures (sample_past, mem_conn, sample_upcoming)
  test_insights.py, test_database.py, test_data.py, test_ingest.py

docs/
  design-system.md    Visual theme, component architecture, CSS gotchas
  analyses.md         Implemented and candidate analyses
```

---

## Code conventions

- **`insights.py`** — pure functions only. Input: DataFrame. Output: DataFrame or scalar. Zero Streamlit.
- **`app.py`** — layout and calls only. No business logic. Use surgical `str_replace` edits (file is long).
- **`i18n.py`** — flat dict, no duplicate keys. Always add both `EN` and `ES` for new keys.
- **`database.py`** — all schema changes go in `init_db()` as `ALTER TABLE` migrations.
- Upserts use `COALESCE` to preserve existing non-null values (logo URLs, images).
- UTC everywhere for datetimes.
- When replacing or deleting existing features, check dependent variables and functions — delete if necessary to avoid orphaned code.

---

## Common commands

```bash
# Activate environment
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Run dashboard
streamlit run dashboard/app.py

# Run tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=src --cov=dashboard --cov-report=term-missing

# Ingest data (dev API, fast)
python src/ingest.py --dev

# Ingest data (production, ~30 sec — automated daily via GitHub Actions at 06:00 UTC)
python src/ingest.py
```

---

## What NOT to do

- Do not add Streamlit imports to `insights.py`.
- Do not duplicate keys in `i18n.py`.
- Do not rewrite `app.py` wholesale — use targeted edits.
- Do not add schema columns without a migration in `init_db()`.
- Do not push without running `python -m pytest` first.
