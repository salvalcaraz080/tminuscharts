# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2026-04-26

Initial public release. Full-featured dashboard with 7 tabs, bilingual EN/ES support, and Mission Control dark/light theme.

### Added

**Dashboard tabs**
- Upcoming tab: 6-month GitHub-style heatmap, weekly mission agenda with T-minus countdowns, "Launches to be confirmed" section for TBD launches
- Trends tab: launch density chart with forecast and hatched overlay bars, 5-year rolling mean, YoY insight, monthly polar chart, success rate area line
- Map tab: global scatter geo by launch pad, Space trade routes Sankey (region → orbit / mission type) with period and dimension controls
- Insights tab: SpaceX / Starlink stacked bar with market share headline, rocket family rise and fall multi-line chart with year-range slider, reliability bubble scatter (volume vs success rate)
- New Space tab: commercial vs government 100% area chart, top 5 by sector, provider diversity line, Falcon 9 turnaround scatter with rolling mean
- Missions tab: orbit distribution donut, orbit evolution area, mission types bar, deep space mission cards
- DIY tab: fully interactive chart builder — H-Bar, V-Bar, Line, Scatter across any dimension with color-by, Top N, sort, labels, log scale, median quadrant lines

**Theme and UI**
- Mission Control dark theme (default) and light theme toggle
- Fonts: Orbitron (headings), Barlow Condensed (body), Share Tech Mono (data)
- All charts via `mc_fig()` — unified Plotly theme, hover cards, T-Minus Charts watermark, downloadable PNG
- Custom chart title widget (Orbitron, embeds in PNG download)
- Next launch banner with T-minus countdown chunks and mission details
- 4 custom KPI cells (total, success rate, this year, upcoming 30d)
- Filters expander: period, rocket, rocket family, provider, country/region, mission type, sector, pad, era

**Data layer**
- `insights.py`: 20+ pure analytical functions
- `database.py`: normalised SQLite schema (launches, rockets, pads, providers), upserts with COALESCE, migration-safe `init_db()`
- `ingest.py`: Launch Library 2 API ingestion with `--dev`, `--refresh`, `--full-history` modes and 429 retry logic
- `data.py`: `@st.cache_data` SQL loaders with UTC datetime parsing
- `i18n.py`: bilingual EN/ES flat dictionary

**Tests**
- 143 tests across `test_insights.py`, `test_database.py`, `test_data.py`, `test_ingest.py`
- Shared fixtures in `conftest.py`
