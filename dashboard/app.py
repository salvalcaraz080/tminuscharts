"""
T-Minus Charts — Dashboard MVP

Run from project root:
    streamlit run dashboard/app.py
"""

from datetime import datetime
from html import escape
from pathlib import Path
import base64

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data import load_launches, load_providers, split_past_upcoming, success_rate
from i18n import make_t
import insights
from theme import THEMES, build_css, chart_palette, geo_layout, heatmap_cell_color, heatmap_cell_path, heatmap_colorscale, orbit_node_colors, plotly_layout, region_color_map, title_color, trace_label_color

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="T-Minus Charts",
    page_icon="dashboard/assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "ui_theme" not in st.session_state:
    st.session_state.ui_theme = "dark"
st.session_state.setdefault("ui_lang_str", "en")
for _old_fk in ("f_region", "f_rocket", "f_pad", "f_sector"):
    st.session_state.pop(_old_fk, None)
st.session_state.setdefault("f_regions", [])
st.session_state.setdefault("f_rockets", [])
st.session_state.setdefault("f_pads", [])
st.session_state.setdefault("f_sectors", [])

# ---------------------------------------------------------------------------
# Logo helper
# ---------------------------------------------------------------------------
def _logo_b64() -> str:
    logo_path = Path(__file__).parent / "assets" / "logo_transparent.png"
    if logo_path.exists():
        return base64.b64encode(logo_path.read_bytes()).decode()
    return ""

_LOGO_B64 = _logo_b64()
_LOGO_SRC = f"data:image/png;base64,{_LOGO_B64}" if _LOGO_B64 else ""


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
df = load_launches()

# ---------------------------------------------------------------------------
# Helper — custom chart title
# ---------------------------------------------------------------------------
def chart_title_widget(key: str, t) -> str:
    """Renders a checkbox + optional text input. Returns title string or ''."""
    show = st.checkbox(t("add_custom_title"), key=f"show_{key}")
    if show:
        return st.text_input(
            "", placeholder=t("chart_title_placeholder"),
            key=f"title_{key}", label_visibility="collapsed",
        )
    return ""


def _ui_theme() -> str:
    return st.session_state.get("ui_theme", "dark")


def apply_title(fig: go.Figure, title: str) -> None:
    """Applies a centered title to a Plotly figure if provided."""
    if title:
        th = _ui_theme()
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(family="Orbitron", size=22, color=title_color(th)),
                x=0.5, xanchor="center",
            )
        )


def _render_launch_card(
    launch: pd.Series,
    *,
    badge: str = "",
    right_html: str = "",
    hero: bool = False,
    from_label: str = "From",
    to_label: str = "To",
) -> str:
    """Reusable launch card using banner layout (lines · optional right panel)."""
    rocket    = escape(str(launch.get("rocket_fullname") or launch.get("rocket_name") or "—"))
    payload   = escape(str(launch.get("launch_name") or launch.get("mission_name") or "—"))
    mtype     = escape(str(launch.get("mission_type") or "—"))
    prov      = escape(str(launch.get("provider_name") or "—"))
    country   = escape(str(launch.get("provider_country") or ""))
    prov_full = f"{prov} ({country})" if country else prov
    pad       = escape(str(launch.get("pad_location") or launch.get("pad_name") or "—"))
    orbit     = escape(str(launch.get("mission_orbit") or "—"))
    desc_raw  = str(launch.get("mission_description") or "")

    badge_html = f'<span class="banner-badge">{escape(badge)}</span>' if badge else ""
    desc_html  = (f'<details class="banner-desc"><summary>▾ 📋 Description</summary><p>{escape(desc_raw)}</p></details>') if desc_raw else ""
    line1 = f'<div class="banner-line1">🚀 <span>{rocket}</span> &nbsp;|&nbsp; 📦 <span>{payload}</span> &nbsp;|&nbsp; 🔭 <span>{mtype}</span></div>'
    line2 = f'<div class="banner-line2">🏢 <span>{prov_full}</span> &nbsp;|&nbsp;📍{escape(from_label)}:<span>{pad}</span>&nbsp;→&nbsp;🪐{escape(to_label)}:<span>{orbit}</span></div>'
    hero_cls    = " mc-banner--hero" if hero else ""
    right_block = f'<div class="banner-countdown">{right_html}</div>' if right_html else ""

    return f'<div class="mc-banner{hero_cls}"><div class="banner-body">{badge_html}{line1}{line2}{desc_html}</div>{right_block}</div>'


t = make_t(st.session_state["ui_lang_str"])


def category_selector(key: str) -> tuple[str, str]:
    """Horizontal radio for Rocket / Family / Provider / Country/Region / Pad.
    Returns (by_key, label) e.g. ("rocket", "Rocket")."""
    opts = [t("rocket"), t("rocket_family"), t("provider"), t("country_region"), t("pad"), t("mission_type")]
    sel = st.radio("", opts, horizontal=True, index=0, key=key, label_visibility="collapsed")
    by = (
        "rocket" if sel == t("rocket")
        else "family" if sel == t("rocket_family")
        else "provider" if sel == t("provider")
        else "country" if sel == t("country_region")
        else "mission_type" if sel == t("mission_type")
        else "pad"
    )
    return by, sel

# ---------------------------------------------------------------------------
# Sidebar — brand, language, appearance
# ---------------------------------------------------------------------------
logo_html = (
    f'<img src="{_LOGO_SRC}" style="width:38px;height:38px;object-fit:contain;flex-shrink:0;">'
    if _LOGO_SRC else '<span style="font-size:28px;">🚀</span>'
)

with st.sidebar:
    st.markdown(
        f"""
    <div class="sidebar-brand-wrap">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
            {logo_html}
            <div class="sidebar-brand-title">T-MINUS<br>CHARTS</div>
        </div>
        <div class="sidebar-brand-tag">{t("tagline_short")}</div>
        <div style="height:1px;background:linear-gradient(to right,rgba(251,191,36,0.45),transparent);margin-top:6px;"></div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="section-label" style="margin:0 0 6px 0;">{t("language")}</div>',
        unsafe_allow_html=True,
    )
    st.radio(
        "",
        ["en", "es"],
        horizontal=True,
        key="ui_lang_str",
        format_func=lambda x: "EN" if x == "en" else "ES",
        label_visibility="collapsed",
    )

    st.markdown(
        f'<div class="section-label" style="margin:0 0 6px 0;">{t("appearance")}</div>',
        unsafe_allow_html=True,
    )
    st.radio(
        "",
        ["dark", "light"],
        horizontal=True,
        key="ui_theme",
        format_func=lambda m: t("theme_dark") if m == "dark" else t("theme_light"),
        label_visibility="collapsed",
    )

st.markdown(build_css(_ui_theme()), unsafe_allow_html=True)

if _LOGO_SRC:
    st.markdown(
        f'<div class="mc-mobile-logo"><img src="{_LOGO_SRC}" alt=""></div>',
        unsafe_allow_html=True,
    )

with st.sidebar:
    st.divider()
    if df.empty:
        st.error(t("no_data"))
        st.stop()
    total_in_db = len(df) if not df.empty else 0
    _dot = THEMES[_ui_theme()]["live_dot"]
    st.markdown(
        f'<div class="mc-live">'
        f'<span style="display:inline-block;width:6px;height:6px;background:{_dot};'
        f'border-radius:50%;margin-right:5px;vertical-align:middle;"></span>'
        f'{t("live_badge", n=total_in_db)}</div>'
        f'<div class="mc-sidebar-source">{t("data_source")}</div>',
        unsafe_allow_html=True,
    )

NEW_SPACE_YEAR = 2010
year_min_data = int(df["year"].dropna().min()) if not df.empty else 1957
year_max_data = int(df["year"].dropna().max()) if not df.empty else 2026

if _LOGO_SRC:
    st.markdown(
        f"""<div class="mc-page-header">
            <img src="{_LOGO_SRC}" alt="T-Minus Charts" style="width:48px;height:48px;object-fit:contain;flex-shrink:0;">
            <div>
                <div class="mc-page-header-title">T-MINUS<br>CHARTS</div>
                <div class="sidebar-brand-tag">{t("tagline_short")}</div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

_, upcoming = split_past_upcoming(df)

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
_now = pd.Timestamp.now(tz="UTC")
_future = upcoming[upcoming["net"] > _now].sort_values("net")

if not _future.empty:
    nxt    = _future.iloc[0]
    _delta = nxt["net"] - _now
    _days  = _delta.days
    _hours = _delta.seconds // 3600
    _mins  = (_delta.seconds % 3600) // 60
    _when  = f"{nxt['net'].strftime('%a')} {nxt['net'].day} {nxt['net'].strftime('%b')} · {nxt['net'].strftime('%H:%M')} UTC"
    _cd_parts = [f"T−{_days:02d}d", f"{_hours:02d}h", f"{_mins:02d}m"]
    _cd_html  = "".join(f'<span class="countdown-chunk">{p}</span>' for p in _cd_parts)
    _right_html = f'<div class="countdown-chunks">{_cd_html}</div><div class="countdown-when">{_when}</div>'
    st.markdown(
        _render_launch_card(
            nxt,
            badge=f"▶ {t('banner_next_label')}",
            right_html=_right_html,
            hero=True,
            from_label=t("from"),
            to_label=t("to"),
        ),
        unsafe_allow_html=True,
    )
else:
    st.info(t("banner_no_upcoming"))

st.markdown("<br>", unsafe_allow_html=True)

with st.expander(t("filters_expander"), expanded=False):
    _cap_col, _btn_col = st.columns([6, 1], vertical_alignment="center")
    with _cap_col:
        st.caption(t("filters_expander_help"))
    with _btn_col:
        if st.button(t("reset_filters"), key="btn_reset_filters", use_container_width=True):
            st.session_state.f_regions = []
            st.session_state.f_families = []
            st.session_state.f_rockets = []
            st.session_state.f_providers = []
            st.session_state.f_mission_types = []
            st.session_state.f_pads = []
            st.session_state.f_sectors = []
            st.session_state.f_period = (year_min_data, year_max_data)
            st.session_state.f_era = t("all")
            st.rerun()

    # Line 1: Year slider (full width)
    year_from, year_to = st.select_slider(
        t("period"),
        options=list(range(year_min_data, year_max_data + 1)),
        value=(year_min_data, year_max_data),
        key="f_period",
    )

    # Line 2: Rocket | Rocket Family
    _fc1, _fc2 = st.columns(2)
    with _fc1:
        rockets_choices = sorted(df["rocket_name"].dropna().unique().tolist())
        st.multiselect(t("rocket"), rockets_choices, key="f_rockets", help=t("filters_multiselect_help"))
    with _fc2:
        families_choices = sorted(df["rocket_family"].dropna().unique().tolist())
        st.multiselect(t("rocket_family"), families_choices, key="f_families", help=t("filters_multiselect_help"))

    # Line 3: Provider | Country-Region
    _fc1, _fc2 = st.columns(2)
    with _fc1:
        providers_choices = sorted(df["provider_name"].dropna().unique().tolist())
        st.multiselect(t("provider"), providers_choices, key="f_providers", help=t("filters_multiselect_help"))
    with _fc2:
        region_choices = sorted(set(insights.COUNTRY_GROUPS.values()))
        st.multiselect(t("country_region"), region_choices, key="f_regions", help=t("filters_multiselect_help"))

    # Line 4: Mission Type | Sector
    _fc1, _fc2 = st.columns(2)
    with _fc1:
        mission_types_choices = sorted(df["mission_type"].dropna().unique().tolist())
        st.multiselect(t("mission_type"), mission_types_choices, key="f_mission_types", help=t("filters_multiselect_help"))
    with _fc2:
        st.multiselect(t("sector"), ["Government", "Private"], key="f_sectors", help=t("filters_multiselect_help"))

    # Line 5: Pad | Era
    _fc1, _fc2 = st.columns(2)
    with _fc1:
        pads_choices = sorted(df["pad_name"].dropna().unique().tolist())
        st.multiselect(t("pad"), pads_choices, key="f_pads", help=t("filters_multiselect_help"))
    with _fc2:
        st.selectbox(t("era"), [t("all"), t("new_space_only")], key="f_era")

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
filtered = df.copy()

regions_sel = st.session_state.get("f_regions") or []
if regions_sel:
    grp = filtered["provider_country"].map(insights.COUNTRY_GROUPS).fillna("Other")
    filtered = filtered[grp.isin(regions_sel)]

families_sel = st.session_state.get("f_families") or []
if families_sel:
    filtered = filtered[filtered["rocket_family"].isin(families_sel)]

rockets_sel = st.session_state.get("f_rockets") or []
if rockets_sel:
    filtered = filtered[filtered["rocket_name"].isin(rockets_sel)]

providers_sel = st.session_state.get("f_providers") or []
if providers_sel:
    filtered = filtered[filtered["provider_name"].isin(providers_sel)]

mission_types_sel = st.session_state.get("f_mission_types") or []
if mission_types_sel:
    filtered = filtered[filtered["mission_type"].isin(mission_types_sel)]

pads_sel = st.session_state.get("f_pads") or []
if pads_sel:
    filtered = filtered[filtered["pad_name"].isin(pads_sel)]

sectors_sel = st.session_state.get("f_sectors") or []
if sectors_sel:
    gov_mask = filtered["provider_type"].fillna("").str.strip() == "Government"
    sector_mask = pd.Series(False, index=filtered.index)
    if "Government" in sectors_sel:
        sector_mask = sector_mask | gov_mask
    if "Private" in sectors_sel:
        sector_mask = sector_mask | ~gov_mask
    filtered = filtered[sector_mask]

selected_era = st.session_state.get("f_era", t("all"))
if selected_era == t("new_space_only"):
    filtered = filtered[filtered["year"] >= NEW_SPACE_YEAR]

filtered = filtered[
    (filtered["year"] >= year_from) & (filtered["year"] <= year_to)
]

f_past, f_upcoming = split_past_upcoming(filtered)
ov_stats = insights.overview_headline_stats(f_past)

# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
rate     = success_rate(f_past)
next_30d = f_upcoming[
    (f_upcoming["net"] <= _now + pd.Timedelta(days=30)) &
    (f_upcoming["status_name"] != "To Be Determined")
]

_cur_year = pd.Timestamp.now().year
this_year_count = int((filtered["year"] == _cur_year).sum())

_yoy_html = ""
if ov_stats and ov_stats.get("yoy_delta_pct") is not None:
    _d = ov_stats["yoy_delta_pct"]
    _yoy_color = THEMES[_ui_theme()]["ok"] if _d >= 0 else THEMES[_ui_theme()]["am"]
    _yoy_arrow = "▲" if _d >= 0 else "▼"
    _yoy_html = f'<div class="kpi-sub"><span style="color:{_yoy_color}">{_yoy_arrow} {abs(_d):.0f}% vs {ov_stats["last_year"]}</span></div>'

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-cell">
        <div class="kpi-label">{t('total_launches')}</div>
        <div class="kpi-value">{len(filtered):,}</div>
        <div class="kpi-sub">{t('kpi_sub_total', from_y=year_from, to_y=year_to)}</div>
        <div class="kpi-corner"></div>
    </div>
    <div class="kpi-cell">
        <div class="kpi-label">{t('success_rate')}</div>
        <div class="kpi-value kv-success">{rate:.1f}%</div>
        <div class="kpi-sub">{t('kpi_sub_success')}</div>
        <div class="kpi-corner"></div>
    </div>
    <div class="kpi-cell">
        <div class="kpi-label">{t('this_year')}</div>
        <div class="kpi-value kv-accent">{this_year_count:,}</div>
        <div class="kpi-sub">{t('kpi_sub_this_year', year=_cur_year)}</div>
        {_yoy_html}
        <div class="kpi-corner"></div>
    </div>
    <div class="kpi-cell">
        <div class="kpi-label">{t('upcoming_30d')}</div>
        <div class="kpi-value kv-accent">{len(next_30d)}</div>
        <div class="kpi-sub">{t('kpi_sub_upcoming')}</div>
        <div class="kpi-corner"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Plotly theme (follows ui_theme)
# ---------------------------------------------------------------------------
def mc_fig(fig: go.Figure, height: int = 380, *,
           xl: str = "", yl: str = "", fmt: str = ":,", sfx: str = "") -> go.Figure:
    """Apply layout, grid, watermark, and hover templates.

    xl / yl: x- and y-axis labels used to build 'Label = value' hover cards.
    fmt: Plotly number-format string (e.g. ':,' or ':.1f').  sfx: appended suffix (e.g. '%').

    Bar orientation and single-vs-multi-trace are auto-detected.
    Scatter/line/area templates are only applied when no bar traces are present, so
    rolling-avg lines on mixed charts keep the template set at add_trace time.
    Charts with hovertext-based scatter (reliability, explorer scatter) are left as-is.
    """
    th = _ui_theme()
    has_title = bool(fig.layout.title.text)
    fig.update_layout(height=height, **plotly_layout(th))
    if has_title:
        fig.update_layout(margin=dict(t=64))
    fig.update_xaxes(showgrid=True, zeroline=False)
    fig.update_yaxes(showgrid=True, zeroline=False)

    _bars     = [tr for tr in fig.data if isinstance(tr, go.Bar)]
    _scatters = [tr for tr in fig.data if tr.type == "scatter"]

    if _bars:
        _is_h  = _bars[0].orientation == "h"
        _multi = len(_bars) > 1
        if xl and yl:
            if _is_h:
                _ht = (f"{yl} = %{{y}}<br>%{{data.name}} = %{{x{fmt}}}{sfx}<extra></extra>" if _multi
                       else f"{yl} = %{{y}}<br>{xl} = %{{x{fmt}}}{sfx}<extra></extra>")
            else:
                _ht = (f"{xl} = %{{x}}<br>%{{data.name}} = %{{y{fmt}}}{sfx}<extra></extra>" if _multi
                       else f"{xl} = %{{x}}<br>{yl} = %{{y{fmt}}}{sfx}<extra></extra>")
        else:
            if _is_h:
                _ht = ("%{y}<br>%{data.name} = %{x:,}<extra></extra>" if _multi
                       else "%{y}<br>%{x:,}<extra></extra>")
            else:
                _ht = ("%{x}<br>%{data.name} = %{y:,}<extra></extra>" if _multi
                       else "%{x}<br>%{y:,}<extra></extra>")
        fig.update_traces(selector=dict(type="bar"), hovertemplate=_ht)

    if _scatters and not _bars and xl and yl:
        _multi_sc = len(_scatters) > 1
        _sc_ht = (f"{xl} = %{{x}}<br>%{{data.name}} = %{{y{fmt}}}{sfx}<extra></extra>" if _multi_sc
                  else f"{xl} = %{{x}}<br>{yl} = %{{y{fmt}}}{sfx}<extra></extra>")
        fig.update_traces(selector=dict(type="scatter"), hovertemplate=_sc_ht)

    fig.update_traces(
        selector=dict(type="pie"),
        hovertemplate=f"%{{label}}<br>{yl or 'Launches'} = %{{value:,}}<br>Share = %{{percent}}<extra></extra>",
    )

    watermark_color = THEMES.get(th, THEMES["dark"])["tx4"]
    fig.add_annotation(
        text="T-minus Charts",
        xref="paper", yref="paper",
        x=1, y=0,
        xanchor="right", yanchor="bottom",
        showarrow=False,
        font=dict(family="Share Tech Mono, monospace", size=10, color=watermark_color),
        opacity=0.8,
    )
    return fig

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab2, tab1, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    t("tab_upcoming"), t("tab_overview"),
    t("tab_map"), t("tab_insights"), t("tab_newspace"), t("tab_missions"),
    t("tab_explorer"),
])

# ── OVERVIEW ─────────────────────────────────────────────────────────────────
with tab1:
    if f_past.empty:
        st.info(t("no_data"))
    else:
        st.markdown(f'<div class="section-label">{t("sec_launches_over_time")}</div>', unsafe_allow_html=True)
        pal = chart_palette(_ui_theme())
        _dens_df = insights.launches_by_year_with_forecast(f_past)
        if not _dens_df.empty:
            _dens_actual = _dens_df[_dens_df["type"] == "actual"]
            _dens_proj = _dens_df[_dens_df["type"].isin(["current_projected", "forecast"])]
            _dens_rolling = _dens_actual["count"].rolling(window=5, min_periods=2).mean().round(1)
            _complete_actual = _dens_actual[_dens_actual["year"] < pd.Timestamp.now(tz="UTC").year]
            if len(_complete_actual) >= 2:
                _last = _complete_actual.iloc[-1]
                _prev = _complete_actual.iloc[-2]
                _yoy = round((_last["count"] - _prev["count"]) / _prev["count"] * 100, 1)
                _yoy_str = f"+{_yoy}%" if _yoy >= 0 else f"{_yoy}%"
                st.markdown(f"**{t('launch_yoy_headline', year=int(_last['year']), count=int(_last['count']), change=_yoy_str, prev_year=int(_prev['year']))}**")
            _now = pd.Timestamp.now(tz="UTC")
            _cur_year = _now.year
            _prev_year = _cur_year - 1
            _prev_cutoff = _now.replace(year=_prev_year)
            _cur_ytd = int((f_past["net"].dt.year == _cur_year).sum())
            _prev_ytd = int(((f_past["net"].dt.year == _prev_year) & (f_past["net"] <= _prev_cutoff)).sum())
            if _cur_ytd > 0 and _prev_ytd > 0:
                _pace_pct = round((_cur_ytd - _prev_ytd) / _prev_ytd * 100, 1)
                _pace_str = f"+{_pace_pct}%" if _pace_pct >= 0 else f"{_pace_pct}%"
                st.markdown(f"**{t('launch_density_headline', cur_year=_cur_year, cur_ytd=_cur_ytd, change=_pace_str, prev_year=_prev_year)}**")
            _ct = chart_title_widget("launches_over_time", t)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=_dens_proj["year"], y=_dens_proj["count"],
                name=t("forecast_label"),
                marker=dict(
                    color=pal["bar_primary"],
                    opacity=0.35,
                    pattern=dict(shape="/", fgcolor=pal["bar_primary"], bgcolor="rgba(0,0,0,0)", size=8, solidity=0.4),
                    line=dict(color=pal["bar_primary"], width=0.5),
                ),
                hovertemplate=f"%{{x}}: %{{y}} ({t('forecast_label')})<extra></extra>",
            ))
            fig.add_trace(go.Bar(
                x=_dens_actual["year"], y=_dens_actual["count"],
                name=t("launches_col"),
                marker=dict(color=pal["bar_primary"], line=dict(width=0)),
                hovertemplate="%{x}: %{y}<extra></extra>",
            ))
            fig.add_trace(go.Scatter(
                x=_dens_actual["year"], y=_dens_rolling,
                name=t("rolling_avg_n", n=5),
                mode="lines", line=dict(color=pal["line_accent"], width=2),
                hovertemplate=f"%{{x}}: %{{y:.1f}} ({t('rolling_avg_n', n=5)})<extra></extra>",
            ))
            fig.update_layout(barmode="overlay")
            apply_title(fig, _ct)
            mc_fig(fig, xl=t("year"), yl=t("launches_col"))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown(f'<div class="section-label">{t("sec_by_category")}</div>', unsafe_allow_html=True)
        _cat_by, _cat_sel = category_selector("overview_category")
        _cat_df = insights.launches_by_category(f_past, by=_cat_by)
        _cat_df.columns = [_cat_sel, t("count")]
        _ct = chart_title_widget("launches_by_category", t)
        fig = px.bar(_cat_df, x=t("count"), y=_cat_sel, orientation="h",
                     color_discrete_sequence=[pal["bar_primary"]])
        apply_title(fig, _ct)
        mc_fig(fig, height=500, xl=t("launches_col"), yl=_cat_sel)
        fig.update_traces(marker_line_width=0)
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f'<div class="section-label">{t("sec_monthly_launches")}</div>', unsafe_allow_html=True)
        _seas_df = insights.monthly_seasonality(f_past)
        if not _seas_df.empty:
            _month_names = (
                ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
                if st.session_state.get("ui_lang_str") == "es"
                else ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            )
            _seas_df["month_label"] = _seas_df["month_num"].apply(lambda m: _month_names[m - 1])
            _peak = _seas_df.loc[_seas_df["avg_launches"].idxmax()]
            _low = _seas_df.loc[_seas_df["avg_launches"].idxmin()]
            st.markdown(f"**{t('monthly_peak_low', peak_month=_month_names[int(_peak['month_num']) - 1], peak_avg=round(_peak['avg_launches'], 1), low_month=_month_names[int(_low['month_num']) - 1], low_avg=round(_low['avg_launches'], 1))}**")
            _ct = chart_title_widget("monthly_seasonality", t)
            fig = go.Figure(go.Barpolar(
                r=_seas_df["avg_launches"],
                theta=_seas_df["month_label"],
                marker_color=pal["bar_secondary"],
                marker_line_width=0,
                hovertemplate="%{theta}: <b>%{r:.1f}</b> " + t("avg_launches") + "<extra></extra>",
            ))
            apply_title(fig, _ct)
            mc_fig(fig, height=420)
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(showticklabels=True, tickfont=dict(size=9)),
                    angularaxis=dict(direction="clockwise"),
                ),
            )
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.markdown(f'<div class="section-label">{t("sec_success_rate_trend")}</div>', unsafe_allow_html=True)
        _sr_df = insights.success_rate_by_year(f_past)
        if not _sr_df.empty:
            _ct = chart_title_widget("success_rate_trend", t)
            _ip = chart_palette(_ui_theme())
            _fill_color = "rgba(34,197,94,0.08)" if _ui_theme() == "dark" else "rgba(27,138,58,0.08)"
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=_sr_df["year"], y=_sr_df["success_rate"],
                mode="lines+markers", name=t("success_rate"),
                line=dict(color=_ip["success"], width=2.5),
                fill="tozeroy", fillcolor=_fill_color,
            ))
            apply_title(fig, _ct)
            mc_fig(fig, height=320, xl=t("year_col"), yl=t("success_rate"), fmt=":.1f", sfx="%")
            fig.update_layout(
                yaxis=dict(range=[0, 105], title=t("reliability_rate")),
                xaxis_title=t("year_col"),
            )
            st.plotly_chart(fig, use_container_width=True)

# ── UPCOMING ──────────────────────────────────────────────────────────────────
with tab2:
    if f_upcoming.empty:
        st.info(t("no_upcoming"))
    else:
        import numpy as np

        _thm    = _ui_theme()
        _hscale = heatmap_colorscale(_thm)
        today      = pd.Timestamp.now(tz="UTC").normalize()
        week_start = today - pd.Timedelta(days=today.weekday())
        n_weeks    = 26
        horizon    = week_start + pd.Timedelta(weeks=n_weeks)
        f_upcoming_confirmed = f_upcoming[f_upcoming["status_name"] != "To Be Determined"].copy()
        window     = f_upcoming_confirmed[
            (f_upcoming_confirmed["net"] >= week_start) &
            (f_upcoming_confirmed["net"] < horizon)
        ].copy()
        _hm_total  = len(window)
        st.markdown(f'<div class="section-label">{t("sec_heatmap_12m", n=_hm_total)}</div>', unsafe_allow_html=True)

        _is_es = st.session_state.get("ui_lang_str") == "es"
        _all_days = (
            ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
            if _is_es else
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        )
        y_labels = [lbl if i in (0, 2, 4, 6) else "" for i, lbl in enumerate(_all_days)]

        matrix = np.zeros((7, n_weeks))
        hover  = [["" for _ in range(n_weeks)] for _ in range(7)]

        if not window.empty:
            window["day_key"]  = window["net"].dt.normalize()
            window["weekday"]  = window["net"].dt.dayofweek
            window["week_idx"] = ((window["day_key"] - week_start).dt.days // 7).astype(int)
            window = window[(window["week_idx"] >= 0) & (window["week_idx"] < n_weeks)]
            grouped = (
                window.groupby(["week_idx", "weekday"])
                .agg(count=("launch_name", "count"),
                     names=("launch_name", lambda x: "<br>• " + "<br>• ".join(escape(str(n)) for n in x)))
                .reset_index()
            )
            for _, row in grouped.iterrows():
                w, d = int(row["week_idx"]), int(row["weekday"])
                matrix[d, w] = row["count"]
                dd = week_start + pd.Timedelta(days=w * 7 + d)
                hover[d][w] = f"<b>{dd.strftime('%a %d %b %Y')}</b><br>Total launches: <b>{int(row['count'])}</b>{row['names']}"

        for w in range(n_weeks):
            for d in range(7):
                if not hover[d][w]:
                    dd = week_start + pd.Timedelta(days=w * 7 + d)
                    hover[d][w] = f"<b>{dd.strftime('%a %d %b %Y')}</b><br>—"

        # X-axis: month labels at the first week of each month
        x_tickvals, x_ticktext = [], []
        for w in range(n_weeks):
            wk_date = week_start + pd.Timedelta(weeks=w)
            if w == 0 or wk_date.month != (week_start + pd.Timedelta(weeks=w - 1)).month:
                x_tickvals.append(w)
                x_ticktext.append(wk_date.strftime('%b'))

        _zmax = max(int(matrix.max()), 3)
        _ct = chart_title_widget("heatmap", t)

        # Invisible heatmap: drives hover detection + colorbar via coloraxis.
        # opacity=0 keeps cells fully transparent while SVG pointer-events still fire.
        # Rounded-rect shapes (layer='below') supply the actual visual rendering.
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=list(range(n_weeks)),
            y=list(range(7)),
            customdata=hover,
            hovertemplate="%{customdata}<extra></extra>",
            coloraxis="coloraxis",
            zmin=0, zmax=_zmax,
            opacity=0,
            xgap=0, ygap=0,
        ))
        fig.update_layout(
            coloraxis=dict(
                colorscale=_hscale,
                cmin=0, cmax=_zmax,
                colorbar=dict(title="", thickness=10, tickfont=dict(color=THEMES[_thm]["tk"], size=9)),
            ),
            shapes=[
                dict(
                    type="path",
                    path=heatmap_cell_path(w, d, h=0.42, r=0.1),
                    fillcolor=heatmap_cell_color(_hscale, matrix[d, w], _zmax),
                    line_width=0,
                    layer="below",
                    xref="x", yref="y",
                )
                for w in range(n_weeks)
                for d in range(7)
            ],
        )
        apply_title(fig, _ct)
        mc_fig(fig, height=220)
        fig.update_layout(
            xaxis=dict(
                tickmode="array",
                tickvals=x_tickvals,
                ticktext=x_ticktext,
                side="top",
                showgrid=False,
            ),
            yaxis=dict(
                tickmode="array",
                tickvals=list(range(7)),
                ticktext=y_labels,
                autorange="reversed",
                showgrid=False,
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f'<div class="section-label">{t("sec_agenda")}</div>', unsafe_allow_html=True)
        _now_ag = pd.Timestamp.now(tz="UTC")
        for i, week in enumerate(insights.upcoming_by_week(f_upcoming_confirmed)):
            title_str = t("week_of",
                          start=f"{week['start'].day} {week['start'].strftime('%b')}",
                          end=f"{week['end'].day} {week['end'].strftime('%b')}")
            cl = t("launch_count_one") if week["count"] == 1 else t("launches_count", n=week["count"])
            with st.expander(f"{title_str} · {cl}", expanded=(i == 0)):
                for _, launch in week["launches"].iterrows():
                    net = launch["net"]
                    delta = net - _now_ag
                    when = f"{net.strftime('%a')} {net.day} {net.strftime('%b')} · {net.strftime('%H:%M')} UTC"
                    if delta.total_seconds() <= 0:
                        _cd_html = f'<span class="countdown-chunk">{t("launching_now")}</span>'
                    else:
                        _d = delta.days
                        _h = delta.seconds // 3600
                        _m = (delta.seconds % 3600) // 60
                        _cd_html = "".join(f'<span class="countdown-chunk">{p}</span>' for p in [f"T−{_d:02d}d", f"{_h:02d}h", f"{_m:02d}m"])
                    _right = f'<div class="countdown-chunks">{_cd_html}</div><div class="countdown-when">{escape(when)}</div>'
                    st.markdown(
                        _render_launch_card(
                            launch,
                            right_html=_right,
                            from_label=t("from"),
                            to_label=t("to"),
                        ),
                        unsafe_allow_html=True,
                    )

        f_upcoming_tbd = f_upcoming[f_upcoming["status_name"] == "To Be Determined"].copy()
        if not f_upcoming_tbd.empty:
            st.markdown(f'<div class="section-label">{t("sec_tbd")}</div>', unsafe_allow_html=True)
            _right_tbd = f'<div class="countdown-when">{t("not_scheduled")}</div>'
            for i, week in enumerate(insights.upcoming_by_week(f_upcoming_tbd)):
                title_str = t("week_of",
                              start=f"{week['start'].day} {week['start'].strftime('%b')}",
                              end=f"{week['end'].day} {week['end'].strftime('%b')}")
                cl = t("launch_count_one") if week["count"] == 1 else t("launches_count", n=week["count"])
                with st.expander(f"{title_str} · {cl}", expanded=(i == 0)):
                    for _, launch in week["launches"].iterrows():
                        st.markdown(
                            _render_launch_card(
                                launch,
                                right_html=_right_tbd,
                                from_label=t("from"),
                                to_label=t("to"),
                            ),
                            unsafe_allow_html=True,
                        )

# ── MAP ───────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown(f'<div class="section-label">{t("map_title")}</div>', unsafe_allow_html=True)
    pads_df = (filtered.dropna(subset=["latitude","longitude"])
               .groupby(["pad_name","pad_location","pad_country","latitude","longitude"])
               .size().reset_index(name=t("count")))
    if pads_df.empty:
        st.info(t("no_data"))
    else:
        _ct  = chart_title_widget("map", t)
        _th  = _ui_theme()
        _cnt_col = t("count")
        fig = px.scatter_geo(pads_df, lat="latitude", lon="longitude", size=_cnt_col,
                             hover_name="pad_name",
                             hover_data={"pad_location":True,"pad_country":True,
                                         _cnt_col:True,"latitude":False,"longitude":False},
                             projection="natural earth",
                             color_discrete_sequence=[chart_palette(_th)["bar_secondary"]])
        apply_title(fig, _ct)
        _g = {
            **geo_layout(_th),
            "showcountries": True,
            "countrycolor": "#2e5070" if _th == "dark" else "#7a92aa",
            "countrywidth": 1.0,
        }
        fig.update_layout(height=520, paper_bgcolor="rgba(0,0,0,0)", geo=_g,
                          margin=dict(t=10, b=10, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    # ── ORBITAL ROUTES ────────────────────────────────────────────────────────
    if not f_past.empty:
        st.divider()

        # Resolve dimension first (needed for title before rendering controls)
        _sk_dim    = st.session_state.get("sankey_dim", t("sankey_dim_orbit"))
        _sk_target = "mission_type" if _sk_dim == t("sankey_dim_mission") else "orbit"
        _sk_title  = t("sankey_title_mission") if _sk_target == "mission_type" else t("sankey_title_orbit")

        # Line 1 — title
        st.markdown(f'<div class="section-label">{_sk_title}</div>', unsafe_allow_html=True)
        # Line 2 — subtitle
        st.caption(t("map_orbital_routes_caption"))
        # Line 3 — selectors
        _c1, _c2 = st.columns(2)
        with _c1:
            _period = st.radio(
                "", [t("sankey_full_period"), t("sankey_by_year")],
                index=1, horizontal=True, key="sankey_period", label_visibility="collapsed",
            )
            _by_year = _period == t("sankey_by_year")
        with _c2:
            _sk_dim = st.radio(
                "", [t("sankey_dim_orbit"), t("sankey_dim_mission")],
                horizontal=True, key="sankey_dim", label_visibility="collapsed",
            )
        # Re-resolve after widgets are rendered
        _sk_target = "mission_type" if _sk_dim == t("sankey_dim_mission") else "orbit"

        # Line 4 — year slicer (conditional)
        if _by_year:
            _sankey_years = sorted(f_past["year"].dropna().unique().astype(int).tolist())
            _sankey_year  = st.select_slider(
                t("year"), options=_sankey_years,
                value=_sankey_years[-1], key="sankey_year",
                label_visibility="collapsed",
            )
            _sankey_past = f_past[f_past["year"] == _sankey_year]
        else:
            _sankey_past = f_past
        _routes = insights.orbital_routes(_sankey_past, target=_sk_target)
        if not _routes.empty:
            _th    = _ui_theme()
            _tc    = THEMES[_th]
            _reg_c = region_color_map(_th)
            _orb_c = orbit_node_colors(_th)
            _area  = chart_palette(_th)["area"]

            _src_order = (_routes.groupby("source")["count"].sum()
                          .sort_values(ascending=False).index.tolist())
            _tgt_order = (_routes.groupby("target")["count"].sum()
                          .sort_values(ascending=False).index.tolist())
            _all_nodes = _src_order + _tgt_order
            _node_idx  = {n: i for i, n in enumerate(_all_nodes)}

            if _sk_target == "orbit":
                _tgt_colors = [_orb_c.get(o, _orb_c["Other"]) for o in _tgt_order]
            else:
                _tgt_colors = [_area[i % len(_area)] for i, _ in enumerate(_tgt_order)]

            _node_colors = (
                [_reg_c.get(s, _reg_c["Other"]) for s in _src_order] + _tgt_colors
            )

            def _hex_rgba(h: str, a: float) -> str:
                h = h.lstrip("#")
                return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})"

            _link_colors = [
                _hex_rgba(_reg_c.get(s, _reg_c["Other"]), 0.4)
                for s in _routes["source"]
            ]

            _fig_s = go.Figure(go.Sankey(
                node=dict(
                    label=_all_nodes,
                    color=_node_colors,
                    pad=18,
                    thickness=20,
                    line=dict(color=_tc["pb"], width=0.5),
                    hovertemplate="%{label}<br>%{value:,} launches<extra></extra>",
                ),
                link=dict(
                    source=[_node_idx[s] for s in _routes["source"]],
                    target=[_node_idx[t] for t in _routes["target"]],
                    value=_routes["count"],
                    color=_link_colors,
                    hovertemplate="%{source.label} → %{target.label}<br>%{value:,} launches<extra></extra>",
                ),
            ))
            _fig_s.update_layout(
                height=460,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Share Tech Mono, monospace", color=_tc["cf"], size=12),
                margin=dict(t=10, b=10, l=10, r=10),
            )
            st.plotly_chart(_fig_s, use_container_width=True)

# ── INSIGHTS ─────────────────────────────────────────────────────────────────
with tab4:
    if f_past.empty:
        st.info(t("no_data"))
    else:
        latest_year = int(f_past["year"].max())

        st.markdown(f'<div class="section-label">🛰️ {t("spacex_starlink_effect")}</div>', unsafe_allow_html=True)
        _sl_year, _spx_pct, _sl_pct = insights.spacex_starlink_share_latest_year(f_past)
        st.markdown(f"**{t('starlink_headline', year=_sl_year, spx_pct=_spx_pct, sl_pct=_sl_pct)}**")
        sl_df = insights.starlink_share_by_year(f_past)
        if not sl_df.empty:
            _ct = chart_title_widget("starlink", t)
            fig = go.Figure()
            _ip = chart_palette(_ui_theme())
            fig.add_trace(go.Bar(x=sl_df["year"], y=sl_df["Starlink"], name="Starlink", marker_color=_ip["starlink_cyan"]))
            fig.add_trace(go.Bar(x=sl_df["year"], y=sl_df["Other SpaceX"], name="Other SpaceX", marker_color=_ip["spacex"]))
            fig.add_trace(go.Bar(x=sl_df["year"], y=sl_df["Rest of World"], name="Rest of World", marker_color=_ip["bar_muted"]))
            fig.update_layout(barmode="stack", xaxis_title=t("year_col"), yaxis_title=t("launches_col"))
            apply_title(fig, _ct)
            mc_fig(fig, xl=t("year_col"), yl=t("launches_col"))
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.markdown(f'<div class="section-label">🚀 {t("sec_rocket_families")}</div>', unsafe_allow_html=True)
        _rfby_df = insights.rocket_family_by_year(f_past)
        if not _rfby_df.empty:
            import plotly.colors as pc
            _rf_years = sorted(_rfby_df["year"].unique().astype(int).tolist())
            _rf_cur_year = pd.Timestamp.now(tz="UTC").year
            _rf_default_to = _rf_years[-1] - 1 if _rf_years[-1] >= _rf_cur_year else _rf_years[-1]
            _rf_default_to = max(_rf_years[0], _rf_default_to)
            _rf_default_from = max(_rf_years[0], _rf_default_to - 9)
            _rf_year_from, _rf_year_to = st.select_slider(
                t("year"), options=_rf_years,
                value=(_rf_default_from, _rf_default_to),
                key="rocket_families_period", label_visibility="collapsed",
            )
            _rfby_filtered = _rfby_df[
                (_rfby_df["year"] >= _rf_year_from) & (_rfby_df["year"] <= _rf_year_to)
            ]
            _rf_families = sorted(_rfby_filtered["family"].unique().tolist())
            # Families still flying in the end year (= "active")
            _rf_had_end  = set(_rfby_filtered[_rfby_filtered["year"] == _rf_year_to]["family"])
            # Any family that appeared in the period but is gone by the end year
            _rf_retired  = sorted(set(_rf_families) - _rf_had_end)
            st.markdown(f"▶️ **{t('rocket_families_active', n=len(_rf_had_end), year_from=_rf_year_from, year_to=_rf_year_to)}**")
            if _rf_retired:
                st.markdown(f"❌ **{t('rocket_families_retired', n_retired=len(_rf_retired), retired=', '.join(_rf_retired))}**")
            else:
                st.markdown(f"❎ **{t('rocket_families_none_retired')}**")
            _ct = chart_title_widget("sec_rocket_families", t)
            _rf_palette = pc.qualitative.Plotly + pc.qualitative.D3
            _rf_color_map = {fam: _rf_palette[i % len(_rf_palette)] for i, fam in enumerate(_rf_families)}
            fig = px.line(
                _rfby_filtered, x="year", y="count", color="family",
                color_discrete_map=_rf_color_map,
                markers=True,
                labels={"year": t("year_col"), "count": t("launches_col"), "family": ""},
            )
            apply_title(fig, _ct)
            mc_fig(fig, height=460, xl=t("year_col"), yl=t("launches_col"))
            fig.update_traces(line=dict(width=2), marker=dict(size=5))
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.markdown(f'<div class="section-label">🎯 {t("sec_reliability")}</div>', unsafe_allow_html=True)
        _rel_df = insights.reliability_by_category(f_past, by="family")
        _rel_df = _rel_df[_rel_df["total"] >= 5]
        if _rel_df.empty:
            st.info(t("no_data"))
        else:
            _ct    = chart_title_widget("reliability", t)
            _ip    = chart_palette(_ui_theme())
            _rcmap = region_color_map(_ui_theme())
            _sizeref = 2.0 * int(_rel_df["total"].max()) / (38.0 ** 2)
            _hover_tmpl = (
                "<b>%{customdata[0]}</b><br>"
                + t("reliability_total") + ": %{x:,}<br>"
                + t("reliability_rate") + ": %{y:.1f}%<extra></extra>"
            )
            fig = go.Figure()
            for _region in sorted(_rel_df["color_group"].unique()):
                _grp = _rel_df[_rel_df["color_group"] == _region]
                fig.add_trace(go.Scatter(
                    x=_grp["total"], y=_grp["success_rate"],
                    mode="markers+text",
                    marker=dict(
                        size=_grp["total"],
                        sizemode="area",
                        sizeref=_sizeref,
                        sizemin=8,
                        color=_rcmap.get(_region, _ip["bar_primary"]),
                        opacity=0.8,
                        line=dict(width=0.5, color="rgba(255,255,255,0.2)"),
                    ),
                    text=_grp["name"],
                    textposition="top center",
                    textfont=dict(size=10),
                    name=_region,
                    customdata=_grp[["name", "total", "successes"]].values,
                    hovertemplate=_hover_tmpl,
                ))
            apply_title(fig, _ct)
            mc_fig(fig, height=540)
            fig.update_layout(
                xaxis_title=t("reliability_total"),
                yaxis=dict(range=[0, 108], title=t("reliability_rate")),
                showlegend=True,
            )
            st.plotly_chart(fig, use_container_width=True)

# ── NEW SPACE ─────────────────────────────────────────────────────────────────
_COUNTRY_FLAGS = {
    "USA":"🇺🇸","CHN":"🇨🇳","RUS":"🇷🇺","IND":"🇮🇳","JPN":"🇯🇵","FRA":"🇫🇷","DEU":"🇩🇪",
    "GBR":"🇬🇧","ITA":"🇮🇹","ESP":"🇪🇸","LUX":"🇱🇺","NZL":"🇳🇿","KOR":"🇰🇷","IRN":"🇮🇷",
    "PRK":"🇰🇵","ISR":"🇮🇱","AUS":"🇦🇺","CAN":"🇨🇦","BRA":"🇧🇷","UKR":"🇺🇦","UAE":"🇦🇪",
    "SGP":"🇸🇬","GUF":"🇬🇫","KAZ":"🇰🇿","PAK":"🇵🇰","ARG":"🇦🇷","NOR":"🇳🇴","SWE":"🇸🇪",
}

with tab5:
    if f_past.empty:
        st.info(t("no_data"))
    else:
        _np = chart_palette(_ui_theme())
        growth = insights.newspace_growth(f_past)

        # ── ANNUAL SHARE ──────────────────────────────────────────────────────
        st.markdown(f'<div class="section-label">{t("sec_newspace_share")}</div>', unsafe_allow_html=True)
        sector_df = insights.sector_by_year(f_past)
        if not sector_df.empty:
            long_df = sector_df.melt(id_vars="year", value_vars=["Commercial","Government"],
                                      var_name="sector_en", value_name="count")
            long_df["sector"] = long_df["sector_en"].map({"Commercial":t("commercial"),"Government":t("government")})
            _ct = chart_title_widget("newspace_share", t)
            if growth["first_year"] and growth["first_year"] != growth["last_year"]:
                st.caption(t("newspace_headline_evolution", **growth))
            else:
                _last = sector_df.iloc[-1]
                st.caption(t("newspace_headline_single", year=int(_last["year"]), pct=_last["commercial_pct"]))
            fig = px.area(long_df, x="year", y="count", color="sector", groupnorm="percent",
                          color_discrete_map={t("commercial"):_np["success"],t("government"):_np["bar_secondary"]},
                          labels={"year":t("year_col"),"count":"%","sector":""})
            apply_title(fig, _ct)
            mc_fig(fig, height=360, xl=t("year_col"), yl=t("pct_launches_axis"), fmt=":.1f", sfx="%")
            fig.update_layout(yaxis_title=t("pct_launches_axis"))
            st.plotly_chart(fig, use_container_width=True)

        # ── ECOSYSTEM DIVERSITY ───────────────────────────────────────────────
        st.markdown(f'<div class="section-label">{t("sec_diversity")}</div>', unsafe_allow_html=True)
        diversity = insights.provider_diversity_by_year(f_past)
        if not diversity.empty:
            diversity["sector_label"] = diversity["sector"].map({"Commercial":t("commercial"),"Government":t("government")})
            _ct = chart_title_widget("diversity_providers", t)
            st.caption(t("sec_diversity_providers"))
            fig = px.bar(diversity, x="year", y="unique_providers", color="sector_label", barmode="stack",
                         color_discrete_map={t("commercial"):_np["success"],t("government"):_np["bar_secondary"]},
                         labels={"year":t("year_col"),"unique_providers":t("unique_providers"),"sector_label":""})
            apply_title(fig, _ct)
            mc_fig(fig, height=300, xl=t("year_col"), yl=t("unique_providers"))
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)

        # ── REUSABILITY REVOLUTION ────────────────────────────────────────────
        st.divider()
        st.markdown(f'<div class="section-label">🔄 {t("sec_turnaround")}</div>', unsafe_allow_html=True)
        _turn_df = insights.falcon9_turnaround(f_past)
        if not _turn_df.empty:
            _turn_latest_year = int(_turn_df["net"].dt.year.max())
            _turn_latest = _turn_df[_turn_df["net"].dt.year == _turn_latest_year]
            _min_days = int(_turn_latest["days"].min()) if not _turn_latest.empty else int(_turn_df["days"].min())
            _total_f9 = len(_turn_df) + 1
            st.markdown(f"**{t('turnaround_headline', year=_turn_latest_year, min_days=_min_days, total=_total_f9)}**")

            _fastest_days = int(_turn_df["days"].min())
            _fastest_date = _turn_df.loc[_turn_df["days"].idxmin(), "net"].strftime("%b %Y")
            _12m_ago = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=365)
            _recent_t = _turn_df[_turn_df["net"] >= _12m_ago]
            _recent_avg = round(float(_recent_t["days"].mean()), 1) if not _recent_t.empty else None
            _base_t = _turn_df[_turn_df["net"].dt.year == 2015]
            _base_avg = round(float(_base_t["days"].mean()), 1) if not _base_t.empty else None

            _tcol1, _tcol2, _tcol3 = st.columns(3)
            with _tcol1:
                st.metric(t("turnaround_fastest"), f"{_fastest_days} {t('days_suffix')}", delta=_fastest_date, delta_color="off")
            with _tcol2:
                if _recent_avg is not None:
                    _delta_vs_base = f"vs {_base_avg}{t('days_suffix')} in 2015" if _base_avg else None
                    st.metric(t("turnaround_recent_avg"), f"{_recent_avg} {t('days_suffix')}", delta=_delta_vs_base, delta_color="inverse")
            with _tcol3:
                if _base_avg is not None:
                    st.metric(t("turnaround_baseline"), f"{_base_avg} {t('days_suffix')}")

            _ip = chart_palette(_ui_theme())
            _ct = chart_title_widget("sec_turnaround", t)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=_turn_df["net"], y=_turn_df["days"],
                mode="markers",
                marker=dict(size=4, color=_ip["bar_secondary"], opacity=0.6),
                name=t("days_label"),
                hovertemplate="%{x|%b %d %Y}<br>" + t("days_label") + ": <b>%{y:.0f}</b><extra></extra>",
            ))
            _rolling_t = _turn_df["days"].rolling(window=20, min_periods=5).mean().round(1)
            fig.add_trace(go.Scatter(
                x=_turn_df["net"], y=_rolling_t,
                mode="lines",
                line=dict(color=_ip["line_accent"], width=2.5),
                name=t("trend_line"),
                hovertemplate=t("trend_line") + ": %{y:.1f}<extra></extra>",
            ))
            apply_title(fig, _ct)
            mc_fig(fig, height=360, yl=t("days_label"))
            fig.update_layout(yaxis_title=t("days_label"), xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

        # ── COMPANIES DIRECTORY ───────────────────────────────────────────────
        st.divider()
        st.markdown(f'<div class="section-label">{t("sec_companies")}</div>', unsafe_allow_html=True)
        _providers_df = load_providers()
        if not _providers_df.empty:
            _providers_df = _providers_df[
                (_providers_df["launch_count"] == 0) |
                (_providers_df["first_launch"].dt.year >= NEW_SPACE_YEAR)
            ]
            _cs, _cc, _ct_col = st.columns([3, 2, 2])
            with _cs:
                _comp_search = st.text_input(t("companies_search_label"), placeholder=t("companies_search_ph"),
                                             key="comp_search")
            with _cc:
                _countries_list = sorted(_providers_df["country"].dropna().unique())
                _sel_countries = st.multiselect(t("filter_country"), _countries_list, key="comp_country")
            with _ct_col:
                _sel_type = st.multiselect(
                    t("sector"), ["Commercial", "Government"], key="comp_type",
                    format_func=lambda x: t("commercial") if x == "Commercial" else t("government"),
                )
            _pf = _providers_df.copy()
            if _comp_search:
                _pf = _pf[_pf["name"].str.contains(_comp_search, case=False, na=False)]
            if _sel_countries:
                _pf = _pf[_pf["country"].isin(_sel_countries)]
            if _sel_type:
                _pf = _pf[_pf["type"].isin(_sel_type)]

            st.caption(t("companies_count", n=len(_pf)))

            _th_c = THEMES.get(_ui_theme(), THEMES["dark"])
            _GRID = 3
            for _ri in range(0, len(_pf), _GRID):
                _slice = _pf.iloc[_ri:_ri + _GRID]
                _gcols = st.columns(_GRID)
                for _ci, (_, _pr) in enumerate(_slice.iterrows()):
                    with _gcols[_ci]:
                        _flag = _COUNTRY_FLAGS.get(str(_pr.get("country") or ""), "🌐")
                        _sbadge = t("commercial") if str(_pr.get("type","")).lower() == "commercial" else t("government")
                        if _pr["launch_count"] == 0:
                            _lstr = t("companies_yet_to_launch")
                        else:
                            _fyr = int(pd.to_datetime(_pr["first_launch"]).year) if pd.notna(_pr["first_launch"]) else "?"
                            _lstr = f"{int(_pr['launch_count'])} {t('launches_col')} · {t('companies_since')} {_fyr}"
                        _logo = str(_pr.get("logo_url") or _pr.get("image_url") or "")
                        _img_html = (
                            f'<img src="{escape(_logo)}" style="width:30px;height:30px;'
                            f'object-fit:contain;border-radius:2px;background:rgba(255,255,255,0.06);padding:3px;" />'
                            if _logo else ""
                        )
                        st.markdown(
                            f'<div style="background:{_th_c["lc"]};border-left:3px solid {_th_c["ldr"]};'
                            f'border-radius:2px;padding:12px 14px;margin-bottom:10px;min-height:88px;">'
                            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">'
                            f'{_img_html}'
                            f'<span style="font-family:Barlow Condensed,sans-serif;font-size:15px;font-weight:600;'
                            f'color:{_th_c["tf"]};line-height:1.2;">{escape(str(_pr["name"]))}</span>'
                            f'</div>'
                            f'<div style="font-family:Share Tech Mono,monospace;font-size:12px;'
                            f'color:{_th_c["tx3"]};line-height:1.8;">'
                            f'{_flag} {escape(str(_pr.get("country") or "—"))}&nbsp;·&nbsp;'
                            f'<span style="color:{_th_c["tx2"]};">{escape(_sbadge)}</span><br>'
                            f'{escape(_lstr)}'
                            f'</div></div>',
                            unsafe_allow_html=True,
                        )

# ── MISSIONS ──────────────────────────────────────────────────────────────────
with tab6:
    if f_past.empty:
        st.info(t("no_data"))
    else:
        _th = _ui_theme()
        _pal = chart_palette(_th)
        _area = _pal["area"]

        purpose_labels = {
            "Connectivity":          t("purpose_connectivity"),
            "Government / Military": t("purpose_gov_mil"),
            "Earth Observation":     t("purpose_earth_obs"),
            "Science & Exploration": t("purpose_science"),
            "Crewed":                t("purpose_crewed"),
            "Resupply":              t("purpose_resupply"),
            "Other":                 t("purpose_other"),
        }
        purpose_colors = {
            t("purpose_connectivity"): _area[0],
            t("purpose_gov_mil"):      _area[1],
            t("purpose_earth_obs"):    _area[2],
            t("purpose_science"):      _area[3],
            t("purpose_crewed"):       _area[4],
            t("purpose_resupply"):     _area[5],
            t("purpose_other"):        _pal["bar_muted"],
        }

        # ── What is space for? ─────────────────────────────────────────────
        st.markdown(f'<div class="section-label">{t("sec_mission_purpose")}</div>', unsafe_allow_html=True)
        purpose_df = insights.mission_purpose_by_year(f_past)
        if not purpose_df.empty:
            purpose_df["label"] = purpose_df["purpose"].map(purpose_labels)
            _ct = chart_title_widget("mission_purpose", t)
            fig = px.area(
                purpose_df, x="year", y="count", color="label",
                color_discrete_map=purpose_colors,
                labels={"year": t("year_col"), "count": t("launches_col"), "label": ""},
            )
            apply_title(fig, _ct)
            mc_fig(fig, height=400, xl=t("year_col"), yl=t("launches_col"))
            st.plotly_chart(fig, use_container_width=True)

        # ── Megaconstellation effect ────────────────────────────────────────
        st.markdown(f'<div class="section-label">{t("sec_megaconstellation")}</div>', unsafe_allow_html=True)
        mega_total, comms_total = insights.megaconstellation_headline(f_past)
        if comms_total > 0:
            mega_pct = round(mega_total / comms_total * 100, 1)
            st.markdown(f"**{t('megaconstellation_headline_txt', mega=mega_total, comms=comms_total, pct=mega_pct)}**")
        mega_df = insights.megaconstellation_by_year(f_past)
        if not mega_df.empty:
            constellation_labels = {
                "Starlink":      t("mega_starlink"),
                "OneWeb":        t("mega_oneweb"),
                "Amazon Kuiper": t("mega_kuiper"),
                "Other Comms":   t("mega_other"),
            }
            constellation_colors = {
                t("mega_starlink"): _pal["starlink_cyan"],
                t("mega_oneweb"):   _area[2],
                t("mega_kuiper"):   _area[3],
                t("mega_other"):    _pal["bar_muted"],
            }
            mega_df["label"] = mega_df["constellation"].map(constellation_labels)
            _ct = chart_title_widget("megaconstellation", t)
            fig = px.bar(
                mega_df, x="year", y="count", color="label",
                color_discrete_map=constellation_colors,
                labels={"year": t("year_col"), "count": t("launches_col"), "label": ""},
                barmode="stack",
            )
            apply_title(fig, _ct)
            mc_fig(fig, height=360, xl=t("year_col"), yl=t("launches_col"))
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)

        # ── Exploration milestones ──────────────────────────────────────────
        st.markdown(f'<div class="section-label">{t("sec_exploration")}</div>', unsafe_allow_html=True)
        deep = insights.deep_space_missions(f_past)
        if not deep.empty:
            _deep_types = sorted(deep["mission_type"].dropna().unique().tolist())
            _sel_types = st.multiselect(
                t("mission_type"), _deep_types, key="mis_exp_types",
                help=t("filters_multiselect_help"),
            )
            if _sel_types:
                deep = deep[deep["mission_type"].isin(_sel_types)]
        if deep.empty:
            st.info(t("deep_space_none"))
        else:
            for _, launch in deep.iterrows():
                net = launch["net"]
                when = net.strftime(f"%a {net.day} %b %Y · %H:%M UTC") if hasattr(net, "strftime") else str(net)
                st.markdown(
                    _render_launch_card(
                        launch,
                        right_html=f'<div class="countdown-when">{escape(when)}</div>',
                        from_label=t("from"),
                        to_label=t("to"),
                    ),
                    unsafe_allow_html=True,
                )

# ── EXPLORER ──────────────────────────────────────────────────────────────────
with tab7:
    if f_past.empty:
        st.info(t("no_data"))
    else:
        pal = chart_palette(_ui_theme())

        st.markdown(f'<p style="font-size:1rem;opacity:0.85;margin-bottom:1.2rem;">{t("explorer_intro")}</p>', unsafe_allow_html=True)

        # ── Section 1: Shared controls ────────────────────────────────────────
        st.markdown(f'<div class="section-label">{t("explorer_sec_main")}</div>', unsafe_allow_html=True)
        s1a, s1b, s1c = st.columns(3)

        with s1a:
            chart_type = st.radio(
                t("explorer_chart_type"),
                [t("explorer_hbar"), t("explorer_vbar"), t("explorer_line"), t("explorer_scatter")],
                key="ex_chart_type",
            )

        with s1b:
            if chart_type != t("explorer_scatter"):
                metric_sel = st.radio(
                    t("explorer_metric"),
                    [t("explorer_count"), t("explorer_success_rate")],
                    key="ex_metric",
                )
                metric_key = "count" if metric_sel == t("explorer_count") else "success_rate"
            else:
                metric_key = "count"

        with s1c:
            _time_opts = [t("year"), t("quarter"), t("month")]
            group_opts = [
                t("provider"), t("rocket_family"), t("rocket"),
                t("country_region"), t("pad"), t("mission_type"),
                t("sector"), t("era"),
            ] + ([] if chart_type == t("explorer_line") else _time_opts)
            group_sel = st.selectbox(t("explorer_group_by"), group_opts, key="ex_group_by")
            group_key = (
                "provider" if group_sel == t("provider")
                else "family" if group_sel == t("rocket_family")
                else "rocket" if group_sel == t("rocket")
                else "country" if group_sel == t("country_region")
                else "pad" if group_sel == t("pad")
                else "mission_type" if group_sel == t("mission_type")
                else "sector" if group_sel == t("sector")
                else "era" if group_sel == t("era")
                else "year" if group_sel == t("year")
                else "quarter" if group_sel == t("quarter")
                else "month"
            )

        # color_by defaults — overridden in section 2 for bar charts
        color_sel = t("explorer_no_split")
        color_by_key = None

        st.markdown("---")

        # ── Section 2: Chart-specific options ────────────────────────────────
        st.markdown(f'<div class="section-label">{t("explorer_sec_secondary")}</div>', unsafe_allow_html=True)
        barmode = "stack"
        show_labels = False
        sort_asc = False
        select_bottom = False
        top_n = 15
        top_n_line = 8
        time_grain = "year"
        grain_sel = t("year")
        min_n = 5

        if chart_type in (t("explorer_hbar"), t("explorer_vbar")):
            n_cats = insights.explorer_group_count(f_past, group_key)
            s2left, s2mid, s2right = st.columns([2, 2, 2])
            with s2left:
                show_labels = st.checkbox(t("explorer_show_labels"), key="ex_show_labels")
                sort_sel = st.radio(
                    t("explorer_sort"),
                    [t("explorer_desc"), t("explorer_asc")],
                    horizontal=True, key="ex_sort",
                )
                sort_asc = sort_sel == t("explorer_asc")
            with s2mid:
                st.markdown(f'<div style="font-size:0.75rem;opacity:0.7;margin-bottom:4px;">{t("explorer_top_bottom_n")}</div>', unsafe_allow_html=True)
                tb_sel = st.radio(
                    "", [t("explorer_top"), t("explorer_bottom")],
                    horizontal=True, key="ex_top_bottom", label_visibility="collapsed",
                )
                select_bottom = tb_sel == t("explorer_bottom")
                top_n = st.slider("", 1, n_cats, n_cats, key="ex_top_n", label_visibility="collapsed")
            with s2right:
                color_opts = [t("explorer_no_split")] + [o for o in group_opts if o != group_sel]
                color_sel = st.selectbox(t("explorer_color_by"), color_opts, key="ex_color_by")
                if color_sel != t("explorer_no_split"):
                    color_by_key = (
                        "provider" if color_sel == t("provider")
                        else "family" if color_sel == t("rocket_family")
                        else "rocket" if color_sel == t("rocket")
                        else "country" if color_sel == t("country_region")
                        else "pad" if color_sel == t("pad")
                        else "mission_type" if color_sel == t("mission_type")
                        else "sector" if color_sel == t("sector")
                        else "era" if color_sel == t("era")
                        else "year" if color_sel == t("year")
                        else "quarter" if color_sel == t("quarter")
                        else "month"
                    )
                if color_by_key:
                    mode_sel = st.radio(
                        t("explorer_barmode"),
                        [t("explorer_stack"), t("explorer_group_bars")],
                        horizontal=True, key="ex_barmode",
                    )
                    barmode = "stack" if mode_sel == t("explorer_stack") else "group"

        elif chart_type == t("explorer_line"):
            n_cats_line = insights.explorer_group_count(f_past, group_key)
            s2a, s2b, *_ = st.columns(4)
            with s2a:
                show_labels = st.checkbox(t("explorer_show_labels"), key="ex_show_labels")
                grain_sel = st.radio(
                    t("explorer_time_grain"),
                    [t("year"), t("quarter"), t("month")],
                    horizontal=True, key="ex_grain",
                )
                time_grain = (
                    "year" if grain_sel == t("year")
                    else "quarter" if grain_sel == t("quarter")
                    else "month"
                )
            with s2b:
                st.markdown(f'<div style="font-size:0.75rem;opacity:0.7;margin-bottom:4px;">{t("explorer_top_bottom_n")}</div>', unsafe_allow_html=True)
                tb_sel_line = st.radio(
                    "", [t("explorer_top"), t("explorer_bottom")],
                    horizontal=True, key="ex_top_bottom_line", label_visibility="collapsed",
                )
                select_bottom = tb_sel_line == t("explorer_bottom")
                top_n_line = st.slider("", 1, n_cats_line, n_cats_line, key="ex_top_n_line", label_visibility="collapsed")

        else:  # scatter
            s2a, *_ = st.columns(4)
            with s2a:
                _max_launches = int(insights._explorer_group(f_past, group_key).value_counts().max())
                min_n = st.slider(t("explorer_min_launches"), 1, max(_max_launches, 1), min(5, _max_launches), key="ex_min_launches")

        st.markdown("---")

        # ── Chart ────────────────────────────────────────────────────────────
        _ct = chart_title_widget("explorer", t)

        if chart_type in (t("explorer_hbar"), t("explorer_vbar")):
            df_ex = insights.explorer_bar(f_past, group_by=group_key, metric=metric_key,
                                          top_n=top_n, color_by=color_by_key, select_bottom=select_bottom)
            if df_ex.empty:
                st.info(t("no_data"))
            else:
                val_label = t("explorer_count") if metric_key == "count" else t("explorer_success_rate")
                is_h = chart_type == t("explorer_hbar")
                has_color = "color" in df_ex.columns
                bar_kwargs = dict(
                    x="value" if is_h else "group",
                    y="group" if is_h else "value",
                    orientation="h" if is_h else "v",
                    labels={"value": val_label, "group": group_sel, "color": color_sel if has_color else ""},
                )
                if has_color:
                    bar_kwargs["color"] = "color"
                    bar_kwargs["barmode"] = barmode
                else:
                    bar_kwargs["color_discrete_sequence"] = [pal["purple"]]
                fig = px.bar(df_ex, **bar_kwargs)
                apply_title(fig, _ct)
                _ex_xl = val_label if is_h else group_sel
                _ex_yl = group_sel if is_h else val_label
                _ex_fmt = ":.1f" if metric_key == "success_rate" else ":,"
                _ex_sfx = "%" if metric_key == "success_rate" else ""
                n_groups = df_ex["group"].nunique()
                if is_h:
                    mc_fig(fig, height=max(360, 28 * n_groups), xl=_ex_xl, yl=_ex_yl, fmt=_ex_fmt, sfx=_ex_sfx)
                    cat_order = "total descending" if sort_asc else "total ascending"
                    fig.update_layout(yaxis={"categoryorder": cat_order})
                else:
                    mc_fig(fig, height=400, xl=_ex_xl, yl=_ex_yl, fmt=_ex_fmt, sfx=_ex_sfx)
                    cat_order = "total ascending" if sort_asc else "total descending"
                    fig.update_layout(xaxis={"categoryorder": cat_order})
                fig.update_traces(marker_line_width=0)
                if show_labels:
                    fmt = ".1f" if metric_key == "success_rate" else ".0f"
                    suffix = "%" if metric_key == "success_rate" else ""
                    axis = "x" if is_h else "y"
                    fig.update_traces(
                        texttemplate=f"%{{{axis}:{fmt}}}{suffix}",
                        textposition="inside" if has_color else "outside",
                    )
                st.plotly_chart(fig, use_container_width=True)

        elif chart_type == t("explorer_line"):
            df_ex = insights.explorer_line(f_past, group_by=group_key, metric=metric_key,
                                           time_grain=time_grain, top_n=top_n_line,
                                           select_bottom=select_bottom)
            if df_ex.empty:
                st.info(t("no_data"))
            else:
                y_label = t("explorer_count") if metric_key == "count" else t("explorer_success_rate")
                fig = px.line(
                    df_ex, x="time", y="value", color="group",
                    labels={"time": grain_sel, "value": y_label, "group": group_sel},
                )
                apply_title(fig, _ct)
                mc_fig(fig, height=400, xl=grain_sel, yl=y_label)
                if show_labels:
                    fmt = ".1f" if metric_key == "success_rate" else ".0f"
                    suffix = "%" if metric_key == "success_rate" else ""
                    fig.update_traces(
                        texttemplate=f"%{{y:{fmt}}}{suffix}",
                        textposition="top center",
                        mode="lines+text",
                    )
                st.plotly_chart(fig, use_container_width=True)

        else:  # scatter
            df_ex = insights.explorer_scatter(f_past, group_by=group_key, min_launches=min_n,
                                              color_by=color_by_key)
            if df_ex.empty:
                st.info(t("no_data"))
            else:
                st.caption(t("explorer_scatter_axes") + "  ·  " + t("explorer_scatter_min_note", n=min_n))
                has_color = "color" in df_ex.columns
                scatter_kwargs = dict(
                    x="launches", y="success_rate",
                    size="launches", hover_name="group", text="group",
                    labels={"launches": t("explorer_count"), "success_rate": t("explorer_success_rate"),
                            "group": group_sel, "color": color_sel if has_color else ""},
                )
                if has_color:
                    scatter_kwargs["color"] = "color"
                else:
                    scatter_kwargs["color_discrete_sequence"] = [pal["purple"]]
                fig = px.scatter(df_ex, **scatter_kwargs, log_x=True)
                apply_title(fig, _ct)
                fig.update_traces(textposition="top center", marker_opacity=0.75)
                mc_fig(fig, height=500)
                fig.update_traces(hovertemplate=f"%{{hovertext}}<br>{t('explorer_count')} = %{{x:,}}<br>{t('explorer_success_rate')} = %{{y:.1f}}%<extra></extra>",
                                  selector=dict(type="scatter"))
                # Quadrant lines at median launch count and median success rate
                median_x = df_ex["launches"].median()
                median_y = df_ex["success_rate"].median()
                line_color = THEMES.get(_ui_theme(), THEMES["dark"])["tx4"]
                fig.add_vline(x=median_x, line_dash="dot", line_color=line_color, line_width=1)
                fig.add_hline(y=median_y, line_dash="dot", line_color=line_color, line_width=1)
                st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    f'<div class="mc-footer">{t("footer", ts=datetime.now().strftime("%Y-%m-%d %H:%M"))}</div>',
    unsafe_allow_html=True,
)
