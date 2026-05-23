# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.5.0] — 2026-05-23

### Added
- **New Space tab · Falcon 9 booster reuse record**: new headline sentence showing the fastest same-booster reuse within the latest year (fallback: all-time); backed by new `falcon9_booster_turnaround()` in `insights.py` — groups launches by `booster_serial`, diffs within each booster
- **Data pipeline · Booster serial tracking**: `launches.booster_serial` column added via `ALTER TABLE` migration in `database.py`; extracted from `launcher_stage[0].launcher.serial_number` in the Launch Library 2 API response and persisted with COALESCE upsert logic; exposed in `data.py` SELECT query
- **Mobile responsiveness**: KPI cards now display in a 2×2 grid on narrow screens (≤ 480 px) instead of 4 stacked rows; Plotly chart legends repositioned to the top on mobile via `inject_mobile_legend_script()` using a same-origin iframe MutationObserver + `plotly_afterplot` event listener per chart; heatmap colorbar moved to bottom on mobile; turnaround 3-metric row fits on one line on mobile via `.kpi-grid-3` custom HTML grid
- **KPI card #3 · YoY delta inline**: the YoY percentage now appears on the same line as "in [year]" instead of on a new line

### Changed
- **New Space tab · Falcon 9 turnaround KPI**: "all-time fastest" now shows the shortest interval between any two *consecutive* Falcon 9 launches (provider cadence, any booster), using `falcon9_turnaround()`; displays hours when result is less than 1 day
- **New Space tab · Falcon 9 booster reuse headline**: separated from the KPI — headline sentence now exclusively tracks same-booster reuse via `falcon9_booster_turnaround()`; also displays hours when result is less than 1 day
- **New Space tab · Turnaround stat callouts**: replaced three `st.metric()` widgets with a custom HTML `.kpi-grid-3` grid for correct mobile layout

---

## [1.4.0] — 2026-05-05

### Added
- **Insights tab · Launch market concentration**: new section with two charts — stacked bar showing USA / China / Rest of World share (%) since 2000, and HHI (Herfindahl-Hirschman Index) line chart with reference lines at 1,500 (moderate) and 2,500 (highly concentrated); headline stats for latest year; backed by `market_share_by_year()` and `market_hhi_by_year()` in `insights.py`

---

## [1.3.0] — 2026-05-03

### Added
- **Missions tab · What is space for?**: stacked area chart classifying all launches into 7 purpose categories (Connectivity, Government/Military, Earth Observation, Science & Exploration, Crewed, Resupply, Other); backed by `mission_purpose_by_year()` and `_PURPOSE_MAP` in `insights.py`
- **Missions tab · The megaconstellation effect**: stacked bar (Starlink / OneWeb / Amazon Kuiper / Other Comms) with headline stat showing what % of communications launches belong to megaconstellations; backed by `megaconstellation_by_year()` and `megaconstellation_headline()`
- **Missions tab · Exploration milestones**: renamed and repositioned deep space mission cards section; added mission_type multiselect filter (options populated dynamically) to drill into specific mission types

### Changed
- **Missions tab**: full redesign — replaced orbit distribution donut, orbit evolution area chart, and mission types bar chart with the three new sections above

### Removed
- `orbit_distribution()`, `orbit_evolution()`, `mission_type_distribution()`, `leo_dominance_headline()` from `insights.py` (Missions tab only, no other consumers)
- Dead i18n keys: `sec_orbit_dist`, `sec_orbit_evo`, `sec_mission_types`, `sec_deep_space`, `orbit_category`, `orbit_leo`, `orbit_meo`, `orbit_geo`, `orbit_heo`, `orbit_beyond`, `orbit_suborbital`, `orbit_other`, `orbit_unknown`
- `orbit_color_map` removed from `app.py` imports (function kept in `theme.py` — still used by Map tab via `orbit_node_colors`)

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
