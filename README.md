# T-Minus Charts 🚀

**Space launch analytics dashboard.** Interactive visualisations built on data from 8,000+ historical launches — designed for journalists, analysts, and space enthusiasts.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-tminuscharts.streamlit.app-blue?logo=streamlit)](https://tminuscharts.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-143%20passing-brightgreen?logo=pytest)](tests/)

---

## What it does

T-Minus Charts turns raw launch data into reusable charts and original analyses:

- **Trends** — launch density, year-over-year growth, monthly seasonality, success rate history
- **Map** — global launch pads with space trade routes Sankey diagram
- **Insights** — SpaceX / Starlink market share, rocket family rise and fall, reliability scatter
- **New Space** — commercial vs government share, Falcon 9 turnaround times
- **Missions** — orbit distribution, mission types, deep space missions
- **Upcoming** — 6-month heatmap and weekly agenda with T-minus countdowns
- **DIY** — fully interactive chart builder (bar, line, scatter) across any dimension

All charts are downloadable as PNG. The dashboard is bilingual (EN / ES).

---

## Quick start

```bash
git clone https://github.com/your-org/tminuscharts
cd tminuscharts
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

The repo includes a pre-populated SQLite database with full launch history. To run the dashboard immediately:

```bash
streamlit run dashboard/app.py
```

To refresh data from the API:

```bash
python src/ingest.py          # Recent and upcoming launches (~15 min)
python src/ingest.py --dev    # Dev API, fast, limited dataset
```

---

## Project structure

```
tminuscharts/
├── dashboard/
│   ├── app.py          # Streamlit UI — layout and widget calls only
│   ├── data.py         # Cached SQL loaders
│   ├── insights.py     # Pure analytical functions (no Streamlit)
│   ├── i18n.py         # Bilingual EN/ES string dictionary
│   └── theme.py        # CSS injection, mc_fig(), Plotly theme
├── src/
│   ├── ingest.py       # API ingestion script (fetch → upsert → SQLite)
│   └── database.py     # Schema, migrations, upsert functions
├── tests/              # 143 tests (pytest)
├── docs/
│   ├── design-system.md   # Visual theme, component architecture, CSS gotchas
│   └── analyses.md        # Implemented and candidate analyses
├── data/
│   └── tminuscharts.db    # SQLite database (committed for zero-infra deploy)
└── .streamlit/
    └── config.toml
```

---

## Deploy to Streamlit Community Cloud

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your GitHub account
3. Select your fork, branch `main`, entry point `dashboard/app.py`
4. Deploy

No environment variables required. The SQLite database is committed to the repo.

---

## Data source

Launch data from [Launch Library 2](https://thespacedevs.com/llapi) by [The Space Devs](https://thespacedevs.com/).

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, code conventions, and how to propose new analyses.

---

## License

[MIT](LICENSE)
