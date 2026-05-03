# T-MINUS CHARTS · CHAT: 🚀 Visual Improvements

> Redesign of existing charts to improve visual impact on X and newsletter
> UX/UI improvements in the dashboard
> Reference: X_STRATEGY.md
> Last updated: 2026-04-29 (Session 15)

---

## CURRENT DESIGN STATE

### Visual theme: Mission Control
The dashboard uses a dark theme inspired by space control rooms and the polygonal aesthetics of species-in-pieces.com.

**Themes:**
- `dark` (default) — Mission Control dark
- `light` — daytime version, togglable via sidebar
- Toggle persists in `st.session_state.ui_theme`
- `config.toml` always keeps `base="dark"` — the light theme is implemented entirely via CSS overrides in `build_css()`

**Fonts (Google Fonts):**
- `Orbitron` (700) — "T-MINUS CHARTS" title in sidebar
- `Barlow Condensed` (400/600/700) — body, missions, names
- `Share Tech Mono` — labels, KPIs, technical data, monospace

**Dark palette (primary):**
- App background: `#06090f`
- Sidebar background: `#040710`
- Banner/charts background: `#07101f`
- Primary text: `#d8e8f5`
- Secondary text: `#7a9db8`, `#6a8fa8`
- Amber accent: `#fbbf24` — used for countdown T-minus, banner badge, sidebar tag
- Blue accent: `#4a9eff`
- Light blue accent: `#7dd3fc`
- Success green: `#4ade80`
- Very subtle text: `#4a6880` (`cbm`), `#2a4a63` (`ft`)
- Chart font (`cf`): `#a0bcd4`
- Chart ticks (`tk`): `#6a8fa8`
- KPI labels (`kl`): `#7a9db8`

**Light palette:**
- App background: `#eef2f7`, sidebar: `#e4eaf3`
- Text: `#0f1b2a`, secondary: `#3d5a73`
- Blue accent: `#1565c0`, amber: `#c77800`, green: `#1b8a3a`
- Select/input background (`selb`): `#ffffff`, borders (`selbr`): `#b8c5d6`
- KPI/widget background (`kt`): `#f8fafc`

**Polygonal shapes:**
- `clip-path: polygon(...)` on launch cards, cd-pill, banner badge
- Diagonal clip-path borders in sidebar and decorative elements

---

## COMPONENT ARCHITECTURE

### Sidebar (width: 260px, padding: 0 12px 0 14px)
- Logo `logo_transparent.png` (38px) + Orbitron title on the same row, vertically aligned
- "Space Launch Analytics" tagline below, full width, amber colour
- Language toggle: EN (default) / ES — `st.radio` horizontal
- Appearance toggle: Dark (default) / Light — `st.radio` horizontal
- Live footer with pulsing green dot + total DB records
- **Filters are NOT in the sidebar** — see Filters Expander section

### Filters Expander (in main content, above the banner)
- `st.expander` collapsed by default, in the main area (not sidebar)
- "Reset filters" button in right column, compact (vertically aligned with caption)
- Layout: 5 rows, each row uses `st.columns(2)` except the year slider (full width)
  - Row 1: Period (select_slider, full width)
  - Row 2: Rocket | Rocket Family
  - Row 3: Provider | Country/Region
  - Row 4: Mission Type | Sector
  - Row 5: Pad | Era
- Era: options "All" | "New Space only" (≥ 2010)
- Session state keys: `f_period`, `f_rockets`, `f_families`, `f_providers`, `f_regions`, `f_mission_types`, `f_sectors`, `f_pads`, `f_era`

### Next launch banner (compact, one row + 3 lines of text)
- Badge: `▶ NEXT LAUNCH` in amber
- Line 1 (Barlow Condensed bold 17px): `📦 [Payload]`
- Line 2 (Share Tech Mono 12px): `🚀 [Rocket] | 🏢 [Provider] | 📍 From: [Pad] → 🪐 To: [Orbit]`
- Countdown right: chunks `T−00d / 06h / 37m` with responsive flex-wrap (each chunk is an independent span)
- No provider logo, no seconds, no rocket image

### KPIs (4 custom HTML cells, no vanilla st.metric)
- Total launches + "between {year_from} and {year_to}" sub-text
- Success rate (green `#4ade80`)
- This year — launches in current calendar year (blue `#7dd3fc`)
- Upcoming 30d (blue `#7dd3fc`)
- Font: Share Tech Mono; labels 11px (`kl` = `#7a9db8`)

### Plotly charts — mc_fig() theme
All charts go through `mc_fig(fig, height=380, *, xl="", yl="", fmt=":,", sfx="")`:
- `paper_bgcolor`: transparent
- `plot_bgcolor`: `#07101f`
- Font: Share Tech Mono, size 13, colour `#a0bcd4`
- Grid: `#0f2035`
- Tick colour: `#6a8fa8`, size 12
- Legend font: size 12
- If a custom title is set, top margin auto-expands to 64px (otherwise 36px)
- **Watermark**: "T-minus Charts" annotation, bottom-right (`xref/yref="paper"`, `x=1, y=0`), Share Tech Mono 10px, colour `tx4`, opacity 0.8 — visible in screenshots and PNG downloads

**Hover card styling** (`hoverlabel` in `plotly_layout()`):
- Dark: `bgcolor` `#0d1929` (`lc`), `bordercolor` `#4a9eff` (`ac`), font Share Tech Mono 12px
- Light: `bgcolor` white, `bordercolor` `#1565c0`

**Hover card content** — `mc_fig` auto-generates `Label = value` templates:
- `xl` / `yl`: x- and y-axis label strings passed at each call site
- `fmt`: Plotly number-format string (default `":,"` for integers; use `":.1f"` for decimals)
- `sfx`: suffix appended after the value (e.g. `"%"`)
- Bar traces: orientation and single/multi-trace auto-detected; multi-trace uses `%{data.name}` as series label
- Scatter/line/area traces: template applied only when **no bar traces** are present (mixed charts keep inline template set at `add_trace` time)
- Pie traces: `%{label}<br>{yl} = %{value:,}<br>Share = %{percent}`
- Two exceptions set their template explicitly after `mc_fig`: reliability scatter and explorer scatter (use `%{hovertext}` as the entity name)

### Mission cards (`.launch-card--media`)
- Horizontal layout: provider logo 64×64px on the left (fallback emoji 🚀)
- Fields: mission name + cd-pill, date, provider + country, rocket, pad
- Optional fields: destination (orbit), mission_type
- Used in: Upcoming tab (weekly agenda) and Missions tab (deep space)
- **Upcoming tab**: right side shows amber `T−XXd / XXh / XXm` chunks + date (`countdown-chunks` format, same as hero banner)
- **Missions tab (deep space)**: date shown as `Wed 12 Apr 2024 · 14:30 UTC`
- Meta font: Share Tech Mono 13px
- Date/time (`.countdown-when`): Share Tech Mono 13px, colour `tx2`

### Custom title widget (on all charts)
- Discrete checkbox above each chart — Share Tech Mono 13px, colour `tx2` (hover: `tx`)
- When activated → `st.text_input` → centred title embedded in the Plotly figure
- Title font: **Orbitron 22px**, colour `tf` (`#eef4fb`) — futuristic/space aesthetic
- Helpers: `chart_title_widget(key, t)` + `apply_title(fig, title)` at the top of app.py
- Unique key per chart to avoid session state conflicts

### Section labels
- Font: Barlow Condensed 600, `font-size: 18px`, uppercase, colour `tx` (`#d8e8f5`)
- Letter-spacing: `.08em`
- Subtle border-bottom: `rgba(255,255,255,0.04)`

---

## TAB STRUCTURE (7 tabs)

**Tab 1 – 📅 Upcoming**
- GitHub-style heatmap: 26-week window, rounded-rect SVG cells, GitHub green colorscale; "N confirmed launches in the next 6 months" title; TBD launches excluded from both heatmap and agenda
- Mission agenda: expandable cards by week, with provider logo (`.launch-card--media`)
- **Launches to be confirmed**: TBD launches grouped by week in collapsible expanders (same pattern as confirmed agenda); "Not scheduled yet" shown instead of a countdown

**Tab 2 – 📈 Trends**
- YoY delta badge on "This year" KPI cell (green ▲ / amber ▼)
- **Launch Density** (replaces "Launches over time"): actual bars + projected/forecast overlay bars with diagonal hatching pattern; 5-year rolling mean line; two insights: YoY% vs previous complete year, and current-year YTD vs same calendar point last year (backed by `launches_by_year_with_forecast`)
- Launches by category: horizontal bar (full width) with Rocket/Rocket Family/Provider/Country/Region/Pad/Mission Type selector — `category_selector("overview_category")`
- **Launches by month**: `go.Barpolar` radial chart (clockwise); one-line insight for busiest and quietest months (backed by `monthly_seasonality`)
- Success rate over time: full-width area line by year (backed by `success_rate_by_year`)

**Tab 3 – Map**
- Scatter geo: size = number of launches, natural earth projection, colours by theme; country borders enabled (`showcountries=True`, `countrywidth=1.0`, themed colour)
- Space trade routes Sankey: provider country (grouped by region, top 8) → orbital destination or mission type; controls: period radio (Full period / By year, defaults By year) + dimension radio (Orbit / Mission type); year slider shown when By year selected; backed by `orbital_routes()` in `insights.py`; node colours from `region_color_map()` and `orbit_node_colors()` in `theme.py`

**Tab 4 – Insights**
- **The SpaceX / Starlink effect**: stacked bar (Starlink / Other SpaceX / Rest of World); headline shows SpaceX% and Starlink% for latest year (backed by `spacex_starlink_share_latest_year`)
- **Rise and fall of rocket families**: multi-line chart, top 12 families (≥5 launches); year-range `select_slider` defaulting to last decade; two-line insight — active count + list of families that disappeared in the selected period (backed by `rocket_family_by_year`)
- **Reliability scatter**: rocket family only, no controls; X = total launches, Y = success rate %, size = total, coloured by region; min. 5 launches filter (backed by `reliability_by_category(by="family")`)

**Tab 5 – New Space**
- **Annual share**: 100% area (Commercial vs Government); insight sentence rendered as `st.caption` below the chart title widget, before the chart
- **Ecosystem diversity**: stacked bar of active providers per year split Commercial vs Government (backed by `provider_diversity_by_year`)
- **Falcon 9 turnaround**: three `st.metric` stat callouts (all-time fastest + date, avg last 12 months vs 2015 baseline) above the scatter + 20-launch rolling mean chart (backed by `falcon9_turnaround`)
- **New Space companies directory**: filterable card grid (name search + country multiselect + sector multiselect); loaded via `load_providers()` in `data.py` which LEFT JOINs all providers against launches to surface zero-launch companies; filtered to providers whose first launch ≥ 2010 (`NEW_SPACE_YEAR`) plus any yet-to-launch; 3-column HTML card grid matching dashboard visual language (logo, name, flag, sector badge, launch count or "Yet to launch")

**Tab 6 – Missions**
- **What is space for?**: stacked area chart by year × purpose category (7 categories: Connectivity, Government/Military, Earth Observation, Science & Exploration, Crewed, Resupply, Other); colours from `chart_palette()["area"]`; purpose mapping defined in `_PURPOSE_MAP` in `insights.py`; backed by `mission_purpose_by_year()`
- **The megaconstellation effect**: stacked bar by year × constellation (Starlink / OneWeb / Amazon Kuiper / Other Comms); headline stat showing mega launches as % of all comms launches; backed by `megaconstellation_by_year()` and `megaconstellation_headline()`; filtered to `mission_type == "Communications"`, classified by keyword in `launch_name`
- **Exploration milestones**: launch cards (`.launch-card--media`) for missions beyond Earth orbit; mission_type multiselect filter (options populated dynamically from results); backed by `deep_space_missions()` using `DEEP_SPACE_KEYWORDS` + `mission_type == "Planetary Science"`; date shown as `Wed 12 Apr 2024 · 14:30 UTC`

**Tab 7 – DIY (🛠️)**
- Fully interactive chart builder. Two sections: Main Parameters (chart type, metric, group by) and Secondary Parameters (chart-specific controls).
- Chart types: H-Bar, V-Bar, Line, Scatter
- Group by dimensions: provider, rocket family, rocket, country/region, pad, mission type, sector, era, year, quarter, month (year/quarter/month excluded for line charts)
- Sector: maps to `provider_type` (Government / Commercial / Private / Multinational)
- Era: derived — year ≥ 2010 → "New Space", otherwise "Classic Space"
- Bar: color by second dimension (stack or group), Top/Bottom N, sort, labels
- Line: time granularity (year/quarter/month), Top/Bottom N, labels, no markers
- Scatter: min launches (dynamic max), log X axis, median quadrant lines

---

## CSS OVERRIDE GOTCHAS — BaseWeb with `base="dark"`

Since `config.toml` forces `base="dark"`, BaseWeb renders its native components with dark colours regardless of our CSS. The `light_main` block inside `build_css()` contains all overrides for the light theme.

**Key rules discovered in Streamlit 1.56:**

- `[data-baseweb="radio"]` and `[data-baseweb="checkbox"]` are the `<label>` element itself — they do not have a nested `<label>`. Selectors with `label>div` never match.

- The **checkbox indicator** (Checkmark) is a `<span>`, not a `<div>`.
  - ✅ Correct selector: `[data-baseweb="checkbox"]>span`
  - ❌ Incorrect: any variant with `>div` or `label>span`

- The **radio outer ring** (RadioMarkOuter) is the first direct child `<div>` of the label.
  - ✅ Correct selector: `[data-baseweb="radio"]>div:first-of-type`

- The **radio inner fill** (RadioMarkInner) is a `<div>` inside the above. In `base="dark"` its colour is `mono1000 = black`.
  - ✅ Correct selector: `[data-baseweb="radio"]>div:first-of-type>div`

- `[role="radio"]` is NOT on the visual indicator — it is on the hidden `<input>`. Using it does not affect appearance.

- Streamlit CSS custom properties (`:root --background-color`, etc.) do not propagate to BaseWeb styles — these are generated by emotion with hardcoded values from the JS theme. Overrides must be direct CSS with `!important`.

---

## STEP 1: IDENTIFY OBJECTIVE

Before starting a new improvement iteration, answer:
1. Are we improving the Dashboard UI or charts for X?
2. Which specific element or chart?
3. Proposals → discussion → conclusion → mockup if applicable

---

## STEP 2: REDESIGN

- Mockup in an interactive widget before touching code
- Iterate mockup until visual validation
- Then code: Plotly + CSS, surgical str_replace in app.py
- Respect MC_LAYOUT and mc_fig() for theme consistency

---

## STEP 3: ITERATION

- Show result in the dashboard
- Iterate until the desired result is achieved

---

## STEP 4: INTEGRATION

- Edit app.py with surgical str_replace (never rewrite completely except for massive changes)
- If there are new keys → add in i18n.py in both languages (ES + EN), without duplicating keys
- Commit + deploy on Streamlit Community Cloud

---

## STEP 5: INSTRUCTIONS UPDATE

- Update this document with relevant changes for future iterations

---

## PENDING / FUTURE IDEAS

- [ ] Live countdown in banner (requires Streamlit ≥ 1.37 with `@st.fragment`)
- [ ] Rocket image in banner on wide screens (logic already prepared: `rocket_image_url` available in DataFrame, CSS media query `min-width: 1100px`)
- [ ] Responsive / mobile
- [ ] Explicit PNG/SVG download button per chart (currently via native Plotly button)
- [ ] Light version of charts for article embeds (white background, adapted colours)
- [ ] Refine "selected" state of radio buttons in light theme (primary blue ring is currently overridden to grey by the CSS override)
