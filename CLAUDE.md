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
- When replacing or deleting existing features, or iterating over the same feature, check and delete orphaned code.

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

---

## End-of-Session Checklist (Before Committing)

Run through this checklist at the end of every working session, before staging any commit.

### Code quality
- Run the full test suite and confirm everything passes.
- Don't left orhpaned code behind, specially after multiple iterations.
- Run linters/formatters and resolve warnings introduced in this session.
- Remove debug prints, commented-out code, and exploratory scaffolding.
- Check that no secrets, credentials, or local-only paths leaked into the diff.

### Tests
- Assess whether new unit tests are needed for the logic added or changed.
- Update existing tests whose expected behaviour has shifted.
- For non-trivial features, consider an integration test, not just unit coverage.

### Documentation
- Determine whether the following key files need updating:
  - `docs/design-system.md` — for architectural or structural changes.
  - `docs/analyses.md` — for new analyses, metrics, or data-model changes.
  - `README.md` — for setup, usage, or user-facing changes.
- Add or update docstrings for new public functions, classes, or modules.

### Changelog
- Add a new entry to `CHANGELOG.md` under the appropriate section (Added / Changed / Fixed / Removed / Deprecated).
- Flag breaking changes explicitly.

### Final review
- Review the full `git diff` before staging; stage hunks intentionally rather than `git add .`.
- Group unrelated changes into separate commits when reasonable.
- Write a commit message that describes the *why*, not just the *what*.