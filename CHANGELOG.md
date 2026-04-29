# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

---

## [1.2.0] — 2026-04-29

### Added
- **Upcoming tab · Launches to be confirmed**: TBD launches now grouped into weekly collapsible expanders (matching the confirmed agenda layout) instead of a flat list, reducing page length
- **New Space tab · Ecosystem diversity**: replaced provider diversity line chart with a stacked bar chart showing active Commercial and Government providers per year
- **New Space tab · Falcon 9 turnaround**: three `st.metric` stat callouts above the scatter chart — all-time fastest turnaround + date, average over the last 12 months, and 2015 baseline average
- **New Space tab · New Space companies directory**: filterable card grid of all launch providers active since 2010, including those yet to launch; searchable by name, filterable by country and sector; cards show logo, country flag, sector badge, and launch count or "Yet to launch"
- `load_providers()` cached SQL loader in `data.py` — LEFT JOINs all providers against launches to surface zero-launch companies alongside launched ones

### Changed
- **New Space tab · Annual share chart**: insight sentence moved from page headline to `st.caption` below the chart title widget, directly above the chart
- **New Space tab · Annual share chart**: removed the standalone headline markdown above the section; insight is now shown inline with the chart

### Removed
- **New Space tab**: Top 5 Commercial and Top 5 Government horizontal bar charts and their section label
- `top_providers_by_sector()` function from `insights.py` and its test class (no longer used)
- Dead i18n keys: `sec_top5_sector`, `sec_diversity_concentration`, `concentration_top3`, `concentration_others`

---

## [1.1.0] — 2026-04-28

### Added
- GitHub Actions workflow (`refresh_db.yml`) for daily automated database refresh at 06:00 UTC — runs `ingest.py`, commits updated `data/tminuscharts.db` back to the repo, triggering a Streamlit redeploy
- **Trends tab · Launches over time**: replaced granularity radio + bar chart with a unified launch density chart — solid bars for actual years, hatched overlay bars for forecast, 5-year rolling mean line, YoY% insight, and YTD pace vs same date last year
- **Trends tab · Monthly launches**: added peak/low insight line showing the highest and lowest average months
- Codebase cleanup: removed 7 orphaned `insights.py` functions, 64 dead `i18n.py` keys, and associated dead test classes; added 8 new test classes covering previously untested functions (143 tests total)

### Fixed
- **Insights tab · Rise and fall of rocket families**: "Disappeared" families now correctly identifies any family that appeared anywhere in the selected period but is absent in the end year (previously only checked families present in the exact start year, causing "None have disappeared" for wide ranges like 1957–2026)
- **Insights tab · Rise and fall of rocket families**: "N active families" count now reflects families still flying in the end year, matching the chart legend (previously counted all families ever in the period, inflating the number by 1 or more)

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
