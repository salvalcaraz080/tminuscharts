# T-MINUS CHARTS · CHAT: 🚀 New Analysis

> Development of original analyses and charts you won't find anywhere else
> Status: Ready
> Reference: X_STRATEGY.md
> Last updated: 2026-05-03 (Session 16)

---

## OBJECTIVE

Generate **new analyses or charts** that:
- Don't appear on Spaceflight Now, n2yo, or existing analyses
- Are unique enough to be an X thread
- Journalists can reuse in articles

---

## IMPLEMENTED ANALYSES

1. ✅ **"Reliability: success rate vs. total launches"** *(Insights tab)*
   - Rocket family only; bubble scatter (X = total, Y = success rate %, size = total, colour = region)
   - Simplified in Session 14 — no controls, family-level only

2. ✅ **"Rise and fall of rocket families"** *(Insights tab)*
   - Multi-line chart, top 12 families (≥5 launches)
   - Year-range slicer defaulting to last decade
   - Two-line insight: active count + list of families that disappeared in the selected period
   - Backed by `rocket_family_by_year()` in `insights.py`

3. ✅ **"Launch density + forecast"** *(Trends tab)*
   - Annual bar chart with current-year projection + two forecast years (hatched bars)
   - 5-year rolling mean line
   - YoY% insight vs previous complete year + YTD pace vs same point last year
   - Linear regression on last 5 complete years; backed by `launches_by_year_with_forecast()`

4. ✅ **"Falcon 9 turnaround"** *(New Space tab)*
   - Days between consecutive Falcon 9 launches as a reusability metric
   - Three stat callouts: all-time fastest turnaround + date, avg last 12 months, avg 2015 baseline
   - Scatter + 20-launch rolling mean below the callouts
   - Backed by `falcon9_turnaround()` in `insights.py`

5. ✅ **"The SpaceX / Starlink effect"** *(Insights tab)*
   - Stacked bar: Starlink / Other SpaceX / Rest of World
   - Headline: SpaceX% and Starlink% share for latest year
   - Backed by `spacex_starlink_share_latest_year()` and `starlink_share_by_year()`

---

## PENDING CANDIDATES

6. **"The return of governments: state vs commercial + projection"**
   - Improvement of the NewSpace tab share chart with projection to 2027
   - Chart: 100% area + trend line
   - Status: NewSpace tab has the base chart; projection not yet added

7. ✅ **"Market concentration: USA / China / Rest + HHI"** *(Insights tab)*
   - Stacked bar (% share) USA / China / Rest of World since 2000
   - HHI line chart with reference lines at 1,500 (moderate) and 2,500 (highly concentrated)
   - Headline stats: combined USA+China share and HHI for latest year
   - Backed by `market_share_by_year()` and `market_hhi_by_year()` in `insights.py`

8. ✅ **"The megaconstellation effect"** *(Missions tab)*
   - Starlink vs OneWeb vs Amazon Kuiper vs Other Comms, launches per year
   - Chart: stacked bar; headline stat (% of comms launches belonging to megaconstellations)
   - Classification by keyword in `launch_name` (no satellite manifest parsing needed)
   - Backed by `megaconstellation_by_year()` and `megaconstellation_headline()`

---

## NEW CANDIDATES (to discuss)

9. **"The busiest week in space history"**
   - Which ISO week had the most launches ever? Evolution of peak-week count by year
   - Chart: bar chart of max weekly launches per year + annotated peak
   - X angle: "Space is getting crowded fast"

10. **"Launch windows by orbit type"**
   - Which months/quarters favour which orbit types? (LEO vs GTO vs SSO seasonality)
   - Chart: heatmap (orbit type × month, colour = avg launches)
   - X angle: "GTO launches cluster in Q4 — here's why"

11. **"Provider concentration over time"** — ✅ Implemented as analysis #7 above

---

## DEVELOPMENT TEMPLATE

For each new analysis:
- SQL / pandas query → pure function in `insights.py`
- Function input: DataFrame of past launches; output: DataFrame or scalar
- Visualisation in `app.py` (surgical edit)
- i18n keys in both EN and ES
- Example X thread outline

---

## STEP 4: INSTRUCTIONS UPDATE

- Update this document after each session with implemented status and new ideas.
