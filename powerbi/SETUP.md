# T-Minus Charts · Power BI Setup

Quick-work report for data exploration, testing and analysis.

---

## 1. Configure Python in Power BI Desktop

File → Options and settings → Options → Python scripting

Set the Python home directory to your virtual environment:
```
C:\Users\salca\proyectos\tminuscharts\venv
```

---

## 2. Load the data

1. **Get Data → Python script**
2. Paste the full contents of `powerbi/get_data.py`
3. Click **OK** — Power BI runs the script and shows a navigator
4. Select all four tables → **Load**

The script loads the four raw tables straight from SQLite with no transformations:

| Table | Description |
|-------|-------------|
| `launches` | Main fact table — one row per launch |
| `providers` | Launch service providers (`launch_service_providers`) |
| `rockets` | Rocket configurations |
| `pads` | Launch pads with coordinates |

Use Power Query to join, filter and transform as needed.

---

## 3. DAX measures

Create these in the **launches** table (right-click → New measure).

```
Total Launches =
COUNTROWS(launches)
```

```
Past Launches =
CALCULATE(COUNTROWS(launches), launches[is_past] = TRUE())
```

```
Upcoming Launches =
CALCULATE(COUNTROWS(launches), launches[is_past] = FALSE())
```

```
Success Rate % =
DIVIDE(
    CALCULATE(COUNTROWS(launches), launches[is_success] = TRUE()),
    CALCULATE(COUNTROWS(launches), launches[is_concluded] = TRUE())
) * 100
```

```
SpaceX Launches =
CALCULATE(COUNTROWS(launches), launches[is_spacex] = TRUE())
```

```
SpaceX % =
DIVIDE([SpaceX Launches], [Total Launches]) * 100
```

```
Starlink Launches =
CALCULATE(COUNTROWS(launches), launches[is_starlink] = TRUE())
```

```
Starlink % =
DIVIDE([Starlink Launches], [Total Launches]) * 100
```

```
Commercial % =
DIVIDE(
    CALCULATE(COUNTROWS(launches), launches[sector] = "Commercial"),
    [Total Launches]
) * 100
```

---

## 4. Report layout (3 pages)

### Page 1 · Overview
Quick health check and top-level numbers.

| Visual | Type | Fields |
|--------|------|--------|
| Total Launches | Card | `[Total Launches]` |
| Success Rate | Card | `[Success Rate %]` |
| SpaceX % | Card | `[SpaceX %]` |
| Upcoming | Card | `[Upcoming Launches]` |
| Launches by year | Clustered bar | Axis: `year` · Values: `[Total Launches]` |
| Status breakdown | Donut | Legend: `status_name` · Values: `[Total Launches]` |
| Top 10 providers | Clustered bar | Axis: `provider_name` · Values: `[Total Launches]` · Top N filter: 10 |

### Page 2 · Analysis
Deeper cuts — orbit, sector, SpaceX effect, geography.

| Visual | Type | Fields |
|--------|------|--------|
| Commercial vs Government by year | Stacked bar | Axis: `year` · Legend: `sector` · Values: `[Total Launches]` |
| Launches by orbit category | Clustered bar | Axis: `orbit_category` · Values: `[Total Launches]` |
| SpaceX vs Rest by year | Stacked bar | Axis: `year` · Legend: `is_spacex` · Values: `[Total Launches]` |
| Launch pads map | Map | Location: `pad_name` · Lat: `latitude` · Long: `longitude` · Size: `[Total Launches]` |
| Success rate by provider | Clustered bar | Axis: `provider_name` · Values: `[Success Rate %]` · Top N filter: 15, min 5 launches |

### Page 3 · Explorer
Raw data table for testing and ad-hoc queries. Add any slicers you need.

| Visual | Type | Fields |
|--------|------|--------|
| Year slicer | Slicer | `year` |
| Provider slicer | Slicer | `provider_name` |
| Orbit slicer | Slicer | `orbit_category` |
| Sector slicer | Slicer | `sector` |
| Status slicer | Slicer | `status_name` |
| Data table | Table | All columns you want to inspect |

---

## 5. Minimalist styling

- **Canvas background:** white (`#FFFFFF`)
- **No visual borders** — set border to Off on all visuals
- **No visual backgrounds** — set background to Off or transparent
- **Font:** Segoe UI throughout
- **Accent colour:** `#4A9EFF` (matches dashboard blue)
- **Title font size:** 11–12px, colour `#3D5A73`
- **Value font size:** 20–24px for cards, 11px for tables
- **Remove gridlines** on all charts
- **Minimal axis labels** — only show year on X axis, hide Y axis title

---

## 6. Refreshing data

When you run a new ingestion (`python src\ingest.py`), refresh the report:

**Home → Refresh**

Power BI re-runs the Python script and pulls the latest data from SQLite.
