# Contributing to T-Minus Charts

---

## Development setup

```bash
git clone https://github.com/salvalcaraz080/tminuscharts
cd tminuscharts
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run dashboard/app.py
```

Run the test suite (must pass before any commit):

```bash
python -m pytest
python -m pytest --cov=src --cov=dashboard --cov-report=term-missing
```

---

## Project architecture

| File | Responsibility |
|---|---|
| `dashboard/app.py` | Streamlit layout and widget calls only — no business logic |
| `dashboard/data.py` | Cached SQL loaders (`load_launches`, `split_past_upcoming`, `success_rate`) |
| `dashboard/insights.py` | Pure analytical functions — input: DataFrame, output: DataFrame or scalar |
| `dashboard/i18n.py` | Flat bilingual dict `{key: {EN: ..., ES: ...}}` |
| `dashboard/theme.py` | CSS injection, `mc_fig()`, Plotly theme tokens |
| `src/ingest.py` | API ingestion: fetch → upsert → SQLite |
| `src/database.py` | Schema definition, migrations, upsert functions |

---

## Code conventions

### `insights.py`
- Pure functions only. No Streamlit imports, ever.
- Input: `pd.DataFrame`. Output: `pd.DataFrame` or scalar.
- Add tests in `tests/test_insights.py` for every new function.

### `app.py`
- Layout and widget calls only. No business logic.
- Use targeted `str_replace` edits — do not rewrite the file wholesale.

### `i18n.py`
- Flat dict, no duplicate keys.
- Every new string needs both `EN` and `ES` entries.

### `database.py`
- All schema changes go in `init_db()` as `ALTER TABLE` migrations.
- Upserts use `COALESCE` to preserve existing non-null values.

### General
- UTC everywhere for datetimes.
- When removing a feature, delete variables and functions dependent on that feature alone — no orphaned code.
- Run `python -m pytest` before every commit.

---

## Adding a new analysis

1. Write a pure function in `dashboard/insights.py` — input: `past` DataFrame, output: DataFrame or scalar.
2. Add tests in `tests/test_insights.py`.
3. Add i18n keys in `dashboard/i18n.py` (both EN and ES).
4. Wire up the chart in `dashboard/app.py` with a targeted edit.
5. Document the analysis in `docs/analyses.md`.

---

## Submitting changes

- Open an issue first for significant changes — alignment before implementation.
- Keep PRs focused: one feature or fix per PR.
- All tests must pass.
- Follow the existing code conventions above.

---

## Reporting a bug or proposing an analysis

Use the GitHub issue templates:
- **Bug report** — unexpected behaviour in the dashboard or ingestion
- **Analysis request** — propose a new chart or analytical angle
