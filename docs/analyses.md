# T-MINUS CHARTS · CHAT: 🚀 New Analysis

> Development of original analyses and charts you won't find anywhere else
> Status: Ready
> Reference: X_STRATEGY.md
> Last updated: 2026-04-25 (Session 14)

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
   - Scatter + 20-launch rolling mean; headline: fastest turnaround in latest year
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

7. **"Satellite constellation explosion"**
   - Starlink vs OneWeb vs Amazon vs others, satellites/month
   - Chart: stacked area
   - Requires satellite payload classification from mission names — not trivial
   - Status: not started; depends on data quality in mission_name field

---

## NEW CANDIDATES (to discuss)

8. **"The busiest week in space history"**
   - Which ISO week had the most launches ever? Evolution of peak-week count by year
   - Chart: bar chart of max weekly launches per year + annotated peak
   - X angle: "Space is getting crowded fast"

9. **"Launch windows by orbit type"**
   - Which months/quarters favour which orbit types? (LEO vs GTO vs SSO seasonality)
   - Chart: heatmap (orbit type × month, colour = avg launches)
   - X angle: "GTO launches cluster in Q4 — here's why"

10. **"Provider concentration over time"**
    - HHI (Herfindahl-Hirschman Index) of launch market concentration by year
    - Chart: line chart of HHI score — rising = more monopolistic, falling = more competitive
    - X angle: "The space launch market is more concentrated than ever"

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
