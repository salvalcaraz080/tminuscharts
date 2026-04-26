"""Theme tokens for Streamlit CSS and Plotly (dark / light)."""
from __future__ import annotations
from typing import Any

THEMES: dict[str, dict[str, str]] = {
    "dark": {
        "app": "#06090f", "side": "#040710", "sb": "#ffffff09", "tx": "#d8e8f5", "tx2": "#7a9db8",
        "tx3": "#6a8fa8", "tx4": "#4a6880", "ac": "#4a9eff", "as": "#7dd3fc", "am": "#fbbf24", "ok": "#4ade80",
        "pb": "#07101f", "pp": "rgba(0,0,0,0)", "gr": "#0f2035", "cf": "#a0bcd4", "tk": "#6a8fa8",
        "lb": "rgba(255,255,255,0.05)", "bn": "#07101f", "kt": "#06090f", "kl": "#7a9db8",
        "kc": "rgba(255,255,255,0.03)", "sb2": "rgba(255,255,255,0.04)", "lc": "#0d1929", "ldr": "#4a9eff",
        "tf": "#eef4fb", "tb": "#040710", "tm": "#3d5870", "selb": "#080d1a", "selbr": "#ffffff0d",
        "selt": "#b8d0e8", "ft": "#2a4a63", "fb": "#ffffff07", "cbm": "#4a6880", "cbh": "#6a8fa8",
        "go": "#06090f", "gl": "#0d1929", "gc": "#1e3550", "cdp": "#0f2035", "br": "#eef4fb", "live_dot": "#22c55e",
    },
    "light": {
        "app": "#eef2f7", "side": "#e4eaf3", "sb": "#c5d0e0", "tx": "#0f1b2a", "tx2": "#3d5a73",
        "tx3": "#5a728a", "tx4": "#64748b", "ac": "#1565c0", "as": "#0277bd", "am": "#c77800", "ok": "#1b8a3a",
        "pb": "#ffffff", "pp": "rgba(0,0,0,0)", "gr": "#e2e8f0", "cf": "#334155", "tk": "#64748b",
        "lb": "rgba(15,23,42,0.08)", "bn": "#ffffff", "kt": "#f8fafc", "kl": "#64748b",
        "kc": "rgba(15,23,42,0.06)", "sb2": "rgba(15,23,42,0.08)", "lc": "#ffffff", "ldr": "#1565c0",
        "tf": "#0f172a", "tb": "#dce6f2", "tm": "#64748b", "selb": "#ffffff", "selbr": "#b8c5d6",
        "selt": "#0f1b2a", "ft": "#94a3b8", "fb": "#cbd5e1", "cbm": "#94a3b8", "cbh": "#64748b",
        "go": "#dbeafe", "gl": "#f1f5f9", "gc": "#94a3b8", "cdp": "#e8f0fa", "br": "#0f172a", "live_dot": "#16a34a",
    },
}


def plotly_layout(theme: str) -> dict[str, Any]:
    c = THEMES.get(theme, THEMES["dark"])
    return dict(
        paper_bgcolor=c["pp"],
        plot_bgcolor=c["pb"],
        font=dict(family="Share Tech Mono, monospace", color=c["cf"], size=13),
        xaxis=dict(gridcolor=c["gr"], linecolor=c["gr"], tickfont=dict(color=c["tk"], size=12)),
        yaxis=dict(gridcolor=c["gr"], linecolor=c["gr"], tickfont=dict(color=c["tk"], size=12)),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=c["cf"], size=12),
            bordercolor=c["lb"],
            borderwidth=1,
        ),
        hoverlabel=dict(
            bgcolor=c["lc"],
            bordercolor=c["ac"],
            font=dict(family="Share Tech Mono, monospace", size=12, color=c["tx"]),
            align="left",
        ),
        margin=dict(t=36, b=12, l=12, r=12),
    )


def geo_layout(theme: str) -> dict[str, Any]:
    c = THEMES.get(theme, THEMES["dark"])
    return dict(
        bgcolor=c["pb"],
        landcolor=c["gl"],
        oceancolor=c["go"],
        showocean=True,
        showland=True,
        showcoastlines=True,
        coastlinecolor=c["gc"],
        showframe=False,
        countrycolor=c["gc"],
    )


def chart_palette(theme: str) -> dict[str, Any]:
    if theme == "light":
        return {
            "bar_primary": "#1565c0",
            "bar_secondary": "#0288d1",
            "bar_muted": "#94a3b8",
            "bar_stack_mid": "#64748b",
            "pie_status": ["#1565c0", "#0288d1", "#26a69a", "#94a3b8", "#cbd5e1"],
            "line_accent": "#c77800",
            "success": "#1b8a3a",
            "spacex": "#c62828",
            "starlink_cyan": "#00838f",
            "area": ["#1565c0", "#c62828", "#c77800", "#1b8a3a", "#7b1fa2", "#ef6c00", "#00897b"],
            "purple": "#6a1b9a",
        }
    return {
        "bar_primary": "#1e5f99",
        "bar_secondary": "#4a9eff",
        "bar_muted": "#2a4a63",
        "bar_stack_mid": "#0f2035",
        "pie_status": ["#1e5f99", "#4a9eff", "#7dd3fc", "#2a4a63", "#0f2035"],
        "line_accent": "#fbbf24",
        "success": "#22c55e",
        "spacex": "#e53935",
        "starlink_cyan": "#00acc1",
        "area": ["#4a9eff", "#e53935", "#fbbf24", "#22c55e", "#a855f7", "#f97316", "#06b6d4"],
        "purple": "#7c3aed",
    }


def heatmap_colorscale(theme: str) -> list[list[Any]]:
    # Sharp break at 0.001 so even 1 launch is clearly distinct from "empty"
    if theme == "light":
        return [[0, "#e2e8f0"], [0.001, "#9be9a8"], [0.33, "#40c463"], [0.66, "#30a14e"], [1, "#216e39"]]
    return [[0, "#131c2b"], [0.001, "#0e4429"], [0.33, "#006d32"], [0.66, "#26a641"], [1, "#39d353"]]


def _blend_hex(c0: str, c1: str, t: float) -> str:
    r0, g0, b0 = int(c0[1:3], 16), int(c0[3:5], 16), int(c0[5:7], 16)
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    return f"#{int(r0+t*(r1-r0)):02x}{int(g0+t*(g1-g0)):02x}{int(b0+t*(b1-b0)):02x}"


def heatmap_cell_color(colorscale: list, value: float, vmax: float) -> str:
    """Return an interpolated hex color for a cell value."""
    t = 0.0 if vmax == 0 else max(0.0, min(1.0, value / vmax))
    for i in range(len(colorscale) - 1):
        t0, c0 = colorscale[i]
        t1, c1 = colorscale[i + 1]
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
            return _blend_hex(c0, c1, f)
    return colorscale[-1][1]


def heatmap_cell_path(cx: float, cy: float, h: float = 0.42, r: float = 0.08) -> str:
    """SVG path for a rounded rectangle centered at (cx, cy)."""
    x0, y0, x1, y1 = cx - h, cy - h, cx + h, cy + h
    return (
        f"M {x0+r},{y0} L {x1-r},{y0} Q {x1},{y0} {x1},{y0+r} "
        f"L {x1},{y1-r} Q {x1},{y1} {x1-r},{y1} "
        f"L {x0+r},{y1} Q {x0},{y1} {x0},{y1-r} "
        f"L {x0},{y0+r} Q {x0},{y0} {x0+r},{y0} Z"
    )


def region_color_map(theme: str) -> dict[str, str]:
    a = chart_palette(theme)["area"]
    muted = chart_palette(theme)["bar_muted"]
    return {
        "USA":         a[0],
        "China":       a[1],
        "Russia":      a[2],
        "Europe":      a[3],
        "India":       a[4],
        "South Korea": a[5],
        "Japan":       a[6],
        "New Zealand": a[6],
        "Iran":        muted,
        "North Korea": muted,
        "Israel":      muted,
        "Other":       muted,
    }


def orbit_node_colors(theme: str) -> dict[str, str]:
    """Colors keyed by normalize_orbit() output strings."""
    if theme == "light":
        return {
            "LEO":          "#1565c0",
            "GEO / GTO":    "#7b1fa2",
            "Beyond Earth": "#e65100",
            "Suborbital":   "#00838f",
            "MEO":          "#6a1b9a",
            "HEO":          "#ad1457",
            "Other":        "#78909c",
        }
    return {
        "LEO":          "#4a9eff",
        "GEO / GTO":    "#9333ea",
        "Beyond Earth": "#f97316",
        "Suborbital":   "#06b6d4",
        "MEO":          "#7c3aed",
        "HEO":          "#db2777",
        "Other":        "#4a6880",
    }


def orbit_color_map(theme: str, t) -> dict[str, str]:
    if theme == "light":
        return {
            t("orbit_leo"): "#1565c0",
            t("orbit_meo"): "#6a1b9a",
            t("orbit_geo"): "#7b1fa2",
            t("orbit_heo"): "#ad1457",
            t("orbit_beyond"): "#e65100",
            t("orbit_suborbital"): "#00838f",
            t("orbit_other"): "#78909c",
            t("orbit_unknown"): "#b0bec5",
        }
    return {
        t("orbit_leo"): "#4a9eff",
        t("orbit_meo"): "#7c3aed",
        t("orbit_geo"): "#9333ea",
        t("orbit_heo"): "#db2777",
        t("orbit_beyond"): "#f97316",
        t("orbit_suborbital"): "#06b6d4",
        t("orbit_other"): "#4a6880",
        t("orbit_unknown"): "#2a4a63",
    }


def title_color(theme: str) -> str:
    return THEMES.get(theme, THEMES["dark"])["tf"]


def trace_label_color(theme: str) -> str:
    return THEMES.get(theme, THEMES["dark"])["tx"]


def build_css(theme: str) -> str:
    c = THEMES.get(theme, THEMES["dark"])
    fnt = (
        "@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined"
        ":opsz,wght,FILL,GRAD@24,400,0,0&display=block');"
        "@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&"
        "family=Barlow+Condensed:wght@300;400;600;700&family=Orbitron:wght@500;700&display=swap');"
    )
    light_main = ""
    if theme == "light":
        # Popovers are often portaled to document.body (not under stMain / .stApp).
        # Override Streamlit's internal CSS vars (set to dark by config.toml base="dark")
        # so BaseWeb checkbox/radio indicators don't inherit black backgrounds.
        light_main = f"""
:root, .stApp{{
  --background-color:{c["app"]}!important;
  --secondary-background-color:{c["kt"]}!important;
  --text-color:{c["tx"]}!important;
  --primary-color:{c["ac"]}!important;
  --font:{c["tx"]}!important;
}}

[data-testid="stHeader"]{{background:{c["app"]}!important;border-bottom:1px solid {c["sb"]}!important;}}
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="popover"] li,
[data-baseweb="popover"] ul,
ul[data-baseweb="menu"],
[data-baseweb="popover"] [role="option"],
[data-baseweb="popover"] [aria-selected]{{
  background-color:{c["selb"]}!important;color:{c["selt"]}!important;border-color:{c["selbr"]}!important;
}}
[data-baseweb="popover"] li:hover,
[data-baseweb="popover"] [aria-selected="true"]{{
  background-color:{c["lb"]}!important;color:{c["tx"]}!important;
}}
[data-baseweb="popover"] li *,
[data-baseweb="popover"] [role="option"] *{{
  color:{c["selt"]}!important;
}}
[data-baseweb="tag"]{{
  background-color:{c["lb"]}!important;color:{c["tx"]}!important;border-color:{c["selbr"]}!important;
}}
[data-baseweb="tag"] *{{
  color:{c["tx"]}!important;
}}
[data-testid="stMain"] [data-baseweb="select"],
[data-testid="stMain"] [data-baseweb="select"]>div,
[data-testid="stMain"] [data-baseweb="select"] div[class*="css"],
[data-testid="stExpander"] [data-baseweb="select"],
[data-testid="stExpander"] [data-baseweb="select"]>div{{
  background-color:{c["selb"]}!important;color:{c["selt"]}!important;border-color:{c["selbr"]}!important;
}}
[data-testid="stMain"] [data-testid="stMultiSelect"] [data-baseweb="select"] span,
[data-testid="stMain"] [data-testid="stMultiSelect"] [data-baseweb="select"] p,
[data-testid="stExpander"] [data-testid="stMultiSelect"] [data-baseweb="select"] span,
[data-testid="stExpander"] [data-testid="stMultiSelect"] [data-baseweb="select"] p,
[data-testid="stMain"] [data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stExpander"] [data-testid="stSelectbox"] [data-baseweb="select"] span{{
  color:{c["selt"]}!important;
}}
[data-testid="stMain"] [data-baseweb="radio"] label,
[data-testid="stMain"] [data-baseweb="radio"] span,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] label span,
[data-testid="stSidebar"] [data-baseweb="radio"] label span{{
  color:{c["tx"]}!important;
}}
[data-testid="stMain"] [data-baseweb="radio"] div[role="radiogroup"]>div,
[data-testid="stSidebar"] [data-baseweb="radio"] div[role="radiogroup"]>div{{
  background:{c["kt"]}!important;border:1px solid {c["selbr"]}!important;
}}
[data-testid="stMain"] [data-baseweb="input"],
[data-testid="stMain"] [data-baseweb="textarea"]{{
  background-color:{c["selb"]}!important;border-color:{c["selbr"]}!important;
}}
[data-testid="stMain"] [data-testid="stWidget"] input,
[data-testid="stMain"] textarea,
[data-testid="stMain"] [data-baseweb="input"] input,
[data-testid="stMain"] [data-baseweb="textarea"] textarea,
[data-testid="stMain"] input[aria-label],
[data-testid="stMain"] input:not([type="checkbox"]):not([type="radio"]){{
  background-color:{c["selb"]}!important;color:{c["selt"]}!important;border-color:{c["selbr"]}!important;
  -webkit-text-fill-color:{c["selt"]}!important;
}}
[data-testid="stMain"] [data-baseweb="input"] input::placeholder,
[data-testid="stMain"] [data-baseweb="textarea"] textarea::placeholder{{
  color:{c["tx3"]}!important;opacity:1!important;
}}
[data-testid="stMain"] [data-testid="stSlider"] [data-baseweb="slider"]>div:first-child,
[data-testid="stExpander"] [data-testid="stSlider"] [data-baseweb="slider"]>div:first-child{{
  background:{c["bn"]}!important;
}}
[data-testid="stExpander"] details{{
  background:{c["bn"]}!important;border:1px solid {c["sb"]}!important;border-radius:8px;
}}
[data-testid="stExpander"] summary{{
  color:{c["tx"]}!important;background:{c["kt"]}!important;border-radius:8px 8px 0 0;
}}
[data-testid="stExpander"] [data-testid="stExpanderDetails"]{{
  background:{c["bn"]}!important;color:{c["tx"]}!important;
}}
[data-testid="stDataFrame"]{{background:{c["bn"]}!important;border:1px solid {c["sb"]}!important;border-radius:6px;}}
[data-testid="stDataFrame"] *{{color:{c["tx"]}!important;}}
[data-testid="stMain"] [data-testid="stCheckbox"] label span,
[data-testid="stMain"] [data-testid="stCheckbox"] label p{{
  color:{c["tx"]}!important;
}}
[data-testid="stMain"] [data-testid="stCheckbox"] p{{
  color:{c["tx2"]}!important;
}}
[data-baseweb="checkbox"]>span{{
  background:{c["selb"]}!important;border-color:{c["selbr"]}!important;
}}
[data-baseweb="radio"]>div:first-of-type{{
  background-color:{c["selbr"]}!important;
}}
[data-baseweb="radio"]>div:first-of-type>div{{
  background-color:{c["selb"]}!important;
}}
[data-testid="stMain"] [data-testid="stMultiSelect"] [data-baseweb="select"]>div{{
  background:{c["selb"]}!important;color:{c["selt"]}!important;border-color:{c["selbr"]}!important;
}}
[data-testid="stMain"] [data-testid="stMultiSelect"] [data-baseweb="select"] input,
[data-testid="stExpander"] [data-testid="stMultiSelect"] [data-baseweb="select"] input{{
  color:{c["selt"]}!important;-webkit-text-fill-color:{c["selt"]}!important;background-color:transparent!important;
}}
[data-testid="stMain"] [data-testid="stButton"] button,
[data-testid="stExpander"] [data-testid="stButton"] button{{
  background:{c["bn"]}!important;color:{c["tx"]}!important;border:1px solid {c["selbr"]}!important;
}}
[data-testid="stMain"] [data-testid="stButton"] button:hover,
[data-testid="stExpander"] [data-testid="stButton"] button:hover{{
  background:{c["lb"]}!important;border-color:{c["ac"]}!important;
}}
[data-testid="stSidebar"] [data-testid="stExpander"] details{{
  background:{c["bn"]}!important;border:1px solid {c["sb"]}!important;border-radius:8px!important;
}}
[data-testid="stSidebar"] [data-testid="stExpander"] summary{{
  color:{c["tx"]}!important;background:{c["kt"]}!important;border-radius:8px 8px 0 0!important;
}}
[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stExpanderDetails"]{{
  background:{c["bn"]}!important;color:{c["tx"]}!important;
}}
[data-testid="stSidebar"] [data-baseweb="popover"] [role="listbox"],
[data-testid="stSidebar"] [data-baseweb="popover"] li{{
  background-color:{c["selb"]}!important;color:{c["selt"]}!important;
}}
[data-testid="stMain"] [data-testid="stTextInput"]>div,
[data-testid="stMain"] [data-testid="stTextInput"] [data-baseweb="form-control-container"],
[data-testid="stMain"] [data-testid="stTextInput"] [data-baseweb="base-input"]{{
  background-color:{c["kt"]}!important;border-color:{c["selbr"]}!important;
}}
[data-testid="stMain"] [data-testid="stTextInput"] [data-baseweb="input"] input{{
  background-color:{c["kt"]}!important;color:{c["selt"]}!important;
  -webkit-text-fill-color:{c["selt"]}!important;
}}
[data-testid="stExpander"] [data-baseweb="select"] div,
[data-testid="stExpander"] [data-baseweb="select"] span,
[data-testid="stMain"] [data-baseweb="select"] div,
[data-testid="stMain"] [data-baseweb="select"] span{{
  color:{c["selt"]}!important;
}}
button[data-testid="stExpandSidebarButton"],
button[data-testid="stExpandSidebarButton"] *{{
  color:{c["tx"]}!important;
}}
[data-testid="stExpandSidebarButton"] span[translate="no"],
[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"],
[data-testid="stSidebarCollapseButton"] span[translate="no"],
[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"]{{
  color:{c["tx"]}!important;
}}
"""
    return f"""<style>
{fnt}
html,body,[class*="css"]{{color:{c["tx"]};}}.stApp{{background:{c["app"]};}}
[data-testid="stSidebar"]{{background:{c["side"]}!important;border-right:1px solid {c["sb"]}!important;width:min(260px,100%)!important;min-width:0!important;margin-left:12px!important;border-radius:0 10px 10px 0!important;}}
[data-testid="stSidebar"]>div:first-child{{padding:0 12px 0 14px!important;}}
[data-testid="stSidebar"] label,[data-testid="stSidebar"] .stRadio label,[data-testid="stSidebar"] p,[data-testid="stSidebar"] span{{font-family:'Share Tech Mono',monospace!important;font-size:12px!important;letter-spacing:.1em;color:{c["tx2"]}!important;text-transform:uppercase;}}
[data-testid="stSidebar"] [data-baseweb="select"]{{background:{c["selb"]}!important;border:1px solid {c["selbr"]}!important;font-family:'Share Tech Mono',monospace!important;font-size:11px!important;}}
[data-testid="stSidebar"] [data-baseweb="select"] div{{background:{c["selb"]}!important;color:{c["selt"]}!important;min-height:24px!important;max-height:24px!important;line-height:24px!important;padding-top:0!important;padding-bottom:0!important;}}
[data-testid="stSidebar"] [data-testid="stSlider"]>div>div>div{{background:{c["ac"]}!important;}}
[data-testid="stSidebar"] hr{{border-color:{c["sb"]}!important;margin:6px 0!important;}}
[data-testid="stTabs"] [data-baseweb="tab-list"]{{background:{c["tb"]};border-bottom:1px solid {c["sb"]};flex-wrap:wrap;}}
[data-testid="stTabs"] [data-baseweb="tab"]{{font-family:'Barlow Condensed',sans-serif!important;font-size:14px!important;letter-spacing:.07em;color:{c["tm"]}!important;padding:8px 12px!important;border-bottom:2px solid transparent;}}
[data-testid="stTabs"] [aria-selected="true"]{{color:{c["tx"]}!important;border-bottom:2px solid {c["ac"]}!important;background:transparent!important;}}
p,span,div,li{{font-family:'Barlow Condensed',sans-serif;color:{c["tx"]};}}
[data-testid="stCheckbox"] p{{font-family:'Share Tech Mono',monospace!important;font-size:13px!important;color:{c["tx2"]}!important;letter-spacing:.05em;display:inline!important;}}
[data-testid="stCheckbox"]:hover p{{color:{c["tx"]}!important;}}
.mc-banner{{background:{c["bn"]};border-left:3px solid {c["am"]};padding:10px 14px;margin-bottom:10px;display:flex;align-items:flex-start;gap:14px;}}
.banner-body{{flex:1;min-width:0;}}
.banner-badge{{font-family:'Share Tech Mono',monospace;font-size:11px;letter-spacing:.18em;color:{c["am"]};text-transform:uppercase;display:block;margin-bottom:4px;}}
.banner-line1{{font-family:'Barlow Condensed',sans-serif;font-size:clamp(15px,4vw,17px);font-weight:600;color:{c["tf"]};line-height:1.25;margin-bottom:2px;}}
.banner-line1 span{{color:{c["tx"]};opacity:.92;}}
.banner-line2{{font-family:'Share Tech Mono',monospace;font-size:clamp(14px,3vw,16px);color:{c["tx3"]};line-height:1.45;}}
.banner-line2 span{{color:{c["tx2"]};}}
.banner-desc{{font-family:'Share Tech Mono',monospace;font-size:14px;color:{c["tx3"]};margin-top:6px;}}
.banner-desc summary{{color:{c["as"]};cursor:pointer;font-size:14px;letter-spacing:.06em;list-style:none;}}
.banner-desc summary::-webkit-details-marker{{display:none;}}
.banner-desc p{{margin:4px 0 0 0;color:{c["tx2"]};line-height:1.5;font-size:14px;}}
.banner-countdown{{flex-shrink:0;text-align:right;display:flex;flex-direction:column;align-items:flex-end;justify-content:center;}}
.countdown-chunks{{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:2px 6px;font-family:'Share Tech Mono',monospace;font-size:clamp(16px,4.5vw,20px);color:{c["am"]};line-height:1.2;}}
.countdown-chunk{{color:{c["am"]}!important;}}
.countdown-when{{font-family:'Share Tech Mono',monospace;font-size:13px;color:{c["tx2"]};margin-top:3px;}}
.kpi-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:{c["sb2"]};border-top:1px solid {c["sb2"]};border-bottom:1px solid {c["sb2"]};margin:0 0 20px 0;}}
.kpi-cell{{background:{c["kt"]};padding:12px 14px;position:relative;overflow:hidden;}}
.kpi-cell::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(to right,transparent,{c["ac"]}33,transparent);}}
.kpi-label{{font-family:'Share Tech Mono',monospace;font-size:11px;letter-spacing:.15em;color:{c["kl"]};text-transform:uppercase;margin-bottom:5px;}}
.kpi-value{{font-family:'Share Tech Mono',monospace;font-size:clamp(18px,4vw,22px);color:{c["tx"]};line-height:1;}}
.kpi-value.kv-accent{{color:{c["as"]};}}.kpi-value.kv-success{{color:{c["ok"]};}}
.kpi-value.kv-warning{{color:{c["am"]};font-size:clamp(14px,3.5vw,16px);word-break:break-word;}}
.kpi-sub{{font-family:'Share Tech Mono',monospace;font-size:11px;color:{c["tx4"]};margin-top:4px;}}
.kpi-sub .hi{{color:{c["ok"]};opacity:.85;}}
.kpi-corner{{position:absolute;bottom:5px;right:6px;border-left:6px solid transparent;border-bottom:6px solid {c["kc"]};}}
.section-label{{font-family:'Barlow Condensed',sans-serif;font-weight:600;font-size:18px;letter-spacing:.08em;color:{c["tx"]};text-transform:uppercase;border-bottom:1px solid {c["sb2"]};padding-bottom:6px;margin-bottom:14px;}}
.launch-card{{background:{c["lc"]};border-left:3px solid {c["ldr"]};padding:12px 16px;margin-bottom:8px;clip-path:polygon(0 0,calc(100% - 8px) 0,100% 8px,100% 100%,8px 100%,0 calc(100% - 8px));}}
.launch-card .mission{{font-family:'Barlow Condensed',sans-serif;font-size:16px;font-weight:600;color:{c["tf"]};margin-bottom:5px;}}
.launch-card .meta{{font-family:'Share Tech Mono',monospace;font-size:13px;color:{c["tx3"]};line-height:1.7;}}
.launch-card .meta strong{{color:{c["tx2"]};}}
.launch-card .cd-pill{{display:inline-block;background:{c["cdp"]};color:{c["as"]};font-family:'Share Tech Mono',monospace;font-size:11px;padding:1px 8px;margin-left:6px;clip-path:polygon(4px 0,100% 0,calc(100% - 4px) 100%,0 100%);}}
.sidebar-brand-wrap{{padding:16px 14px 12px;border-bottom:1px solid {c["sb"]};}}
.sidebar-brand-title{{font-family:'Orbitron',sans-serif;font-size:13px;font-weight:700;letter-spacing:.07em;color:{c["br"]};line-height:1.25;}}
.sidebar-brand-tag{{font-family:'Share Tech Mono',monospace;font-size:10px;color:{c["am"]};letter-spacing:.15em;}}
.mc-footer{{font-family:'Share Tech Mono',monospace;font-size:12px;color:{c["ft"]};padding:12px 0;border-top:1px solid {c["fb"]};}}
.mc-live{{font-family:'Share Tech Mono',monospace;font-size:12px;color:{c["tx4"]};padding:4px 0;}}
.mc-sidebar-source{{font-family:'Share Tech Mono',monospace;font-size:10px;color:{c["tx4"]};padding:2px 0 8px 0;line-height:1.5;}}
.mc-page-header{{display:flex;align-items:center;gap:14px;padding:8px 0 16px 0;border-bottom:1px solid {c["sb"]};margin-bottom:18px;}}
.mc-page-header-title{{font-family:'Orbitron',sans-serif;font-size:17px;font-weight:700;letter-spacing:.07em;color:{c["br"]};line-height:1.2;}}
[data-testid="stSidebarCollapseButton"],
button[data-testid="stSidebarCollapseButton"],
[data-testid="stExpandSidebarButton"],
button[data-testid="stExpandSidebarButton"]{{opacity:1!important;}}
[data-testid="stExpandSidebarButton"] span[translate="no"],
[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"],
[data-testid="stSidebarCollapseButton"] span[translate="no"],
[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"]{{
  font-family:'Material Symbols Rounded',sans-serif!important;
  font-size:1.35rem!important;font-weight:400!important;line-height:1!important;
  font-variation-settings:'FILL' 0,'wght' 400,'GRAD' 0,'opsz' 24!important;
  -webkit-font-smoothing:antialiased!important;color:{c["tx2"]}!important;
}}
.st-key-btn_reset_filters [data-testid="stButton"] button,
.st-key-btn_reset_filters [data-testid="stButton"]>div>button,
[data-testid="stExpanderDetails"] [data-testid="stHorizontalBlock"]:first-child [data-testid="column"]:nth-child(2) [data-testid="stButton"] button{{
  width:auto!important;min-width:0!important;max-width:100%!important;
  min-height:2rem!important;padding:0.2rem 0.55rem!important;
  font-size:12px!important;line-height:1.2!important;white-space:nowrap!important;
}}
.mc-mobile-logo{{display:none;pointer-events:none;}}
.mc-mobile-logo img{{display:block;width:32px;height:32px;object-fit:contain;}}
@media(max-width:768px){{
.mc-mobile-logo{{display:flex;position:fixed;top:12px;left:52px;z-index:1000002;align-items:center;justify-content:center;width:36px;height:36px;}}
}}
.mc-banner--hero{{border-left-width:4px;padding:12px 16px;}}
.mc-banner .launch-card-media{{flex:0 0 56px;width:56px;height:56px;min-width:56px;min-height:56px;display:flex;align-items:center;justify-content:center;align-self:center;background:rgba(74,158,255,0.08);border-radius:2px;}}
.mc-banner .launch-card-media-img{{max-width:78%;max-height:78%;width:auto;height:auto;object-fit:contain;}}
.mc-banner .launch-card-media-fallback{{font-size:1.25rem;line-height:1;opacity:0.85;}}
.launch-card--media{{display:flex;flex-direction:row;align-items:center;padding:0;margin-bottom:10px;background:{c["lc"]};border-left:3px solid {c["ldr"]};overflow:hidden;clip-path:none;border-radius:2px;}}
.launch-card--media .launch-card-media{{
  flex:0 0 64px;width:64px;height:64px;min-width:64px;min-height:64px;max-width:64px;max-height:64px;
  display:flex;align-items:center;justify-content:center;align-self:center;
  background:rgba(74,158,255,0.08);
}}
.launch-card--media .launch-card-media-img{{max-width:78%;max-height:78%;width:auto;height:auto;object-fit:contain;}}
.launch-card--media .launch-card-media-fallback{{font-size:1.25rem;line-height:1;opacity:0.85;}}
.launch-card--media .launch-card-content{{flex:1;min-width:0;padding:12px 14px 12px 10px;}}
.launch-card--media .mission{{margin-bottom:6px;}}
@media(max-width:900px){{.kpi-grid{{grid-template-columns:repeat(2,1fr);}}}}
@media(max-width:640px){{.mc-banner{{flex-direction:column;align-items:stretch;}}.banner-countdown{{align-items:flex-start;text-align:left;}}.countdown-chunks{{justify-content:flex-start;}}}}
@media(max-width:480px){{.kpi-grid{{grid-template-columns:1fr;}}}}
@media(max-width:768px){{
[data-testid="stPlotlyChart"]{{overflow-x:auto!important;max-width:100%;-webkit-overflow-scrolling:touch;}}
[data-testid="stPlotlyChart"] .js-plotly-plot{{min-width:620px!important;}}
}}
{light_main}
</style>"""