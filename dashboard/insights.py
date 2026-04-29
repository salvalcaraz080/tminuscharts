"""
T-Minus Charts — Reusable analytical functions.

Each function takes a DataFrame of past launches and returns a
narrative-ready DataFrame for charts or newsletter content.
"""

import pandas as pd


COUNTRY_GROUPS = {
    "USA": "USA", "CHN": "China", "RUS": "Russia", "IND": "India",
    "JPN": "Japan", "FRA": "Europe", "DEU": "Europe", "ITA": "Europe",
    "ESP": "Europe", "GBR": "Europe", "LUX": "Europe", "IRN": "Iran",
    "PRK": "North Korea", "KOR": "South Korea", "ISR": "Israel",
    "NZL": "New Zealand",
}


# ---------------------------------------------------------------------------
# 4. Top launch pads
# ---------------------------------------------------------------------------
def top_pads(past: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return the top N most active launch pads."""
    if past.empty:
        return pd.DataFrame(columns=["pad_name", "pad_location", "pad_country", "count"])

    return (
        past.dropna(subset=["pad_name"])
        .groupby(["pad_name", "pad_location", "pad_country"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(n)
    )


# ---------------------------------------------------------------------------
# 5. Orbital routes (country → orbit category Sankey)
# ---------------------------------------------------------------------------
def orbital_routes(past: pd.DataFrame, top_n: int = 8,
                   target: str = "orbit") -> pd.DataFrame:
    """Source/target/count rows for a provider-country → orbit/mission Sankey.

    target: "orbit" uses normalize_orbit categories;
            "mission_type" uses the raw mission_type column.
    """
    if past.empty:
        return pd.DataFrame(columns=["source", "target", "count"])
    df = past.copy()
    df["region"] = df["provider_country"].map(COUNTRY_GROUPS).fillna("Other")
    if target == "mission_type":
        df["target_val"] = df["mission_type"].fillna("Unknown")
    else:
        df["target_val"] = df["mission_orbit"].apply(normalize_orbit)
    df = df[df["target_val"] != "Unknown"]
    top_regions = (
        df.groupby("region").size()
        .sort_values(ascending=False).head(top_n).index.tolist()
    )
    df = df[df["region"].isin(top_regions)]
    return (
        df.groupby(["region", "target_val"])
        .size().reset_index(name="count")
        .rename(columns={"region": "source", "target_val": "target"})
    )


# ---------------------------------------------------------------------------
# 6. Starlink factor
# ---------------------------------------------------------------------------
def starlink_share_by_year(past: pd.DataFrame) -> pd.DataFrame:
    """Return yearly count of Starlink vs Other SpaceX vs Rest of World."""
    if past.empty:
        return pd.DataFrame(columns=["year", "Starlink", "Other SpaceX", "Rest of World"])

    df = past.copy()
    is_spacex = df["provider_name"].fillna("").str.contains("SpaceX", case=False)
    is_starlink = (
        df["launch_name"].fillna("").str.contains("Starlink", case=False)
        | df["mission_name"].fillna("").str.contains("Starlink", case=False)
    )

    def classify(row_idx):
        if is_starlink.iloc[row_idx]:
            return "Starlink"
        if is_spacex.iloc[row_idx]:
            return "Other SpaceX"
        return "Rest of World"

    df["category"] = [classify(i) for i in range(len(df))]

    grouped = (
        df.groupby(["year", "category"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    for col in ("Starlink", "Other SpaceX", "Rest of World"):
        if col not in grouped.columns:
            grouped[col] = 0
    return grouped.sort_values("year")


def starlink_total_share(past: pd.DataFrame) -> tuple[int, int, float]:
    """Total Starlink launches, total launches, % of global."""
    if past.empty:
        return 0, 0, 0.0
    is_starlink = (
        past["launch_name"].fillna("").str.contains("Starlink", case=False)
        | past["mission_name"].fillna("").str.contains("Starlink", case=False)
    )
    starlink_count = int(is_starlink.sum())
    total = len(past)
    pct = (starlink_count / total * 100) if total else 0.0
    return starlink_count, total, round(pct, 1)


def spacex_starlink_share_latest_year(past: pd.DataFrame) -> tuple[int, float, float]:
    """Return (year, spacex_pct, starlink_pct) for the most recent year in data."""
    if past.empty:
        return 0, 0.0, 0.0
    latest_year = int(past["year"].max())
    year_df = past[past["year"] == latest_year]
    total = len(year_df)
    if total == 0:
        return latest_year, 0.0, 0.0
    is_spacex = year_df["provider_name"].fillna("").str.contains("SpaceX", case=False)
    is_starlink = (
        year_df["launch_name"].fillna("").str.contains("Starlink", case=False)
        | year_df["mission_name"].fillna("").str.contains("Starlink", case=False)
    )
    spacex_pct = round(is_spacex.sum() / total * 100, 1)
    starlink_pct = round(is_starlink.sum() / total * 100, 1)
    return latest_year, spacex_pct, starlink_pct


# ---------------------------------------------------------------------------
# 6. New Space vs Government
# ---------------------------------------------------------------------------
def _classify_sector(provider_type) -> str:
    """Map raw provider_type to binary category: Government vs Commercial."""
    if not provider_type or pd.isna(provider_type):
        return "Commercial"
    return "Government" if str(provider_type).strip() == "Government" else "Commercial"


def sector_by_year(past: pd.DataFrame) -> pd.DataFrame:
    """Yearly breakdown Commercial vs Government launches."""
    if past.empty:
        return pd.DataFrame(columns=["year", "Commercial", "Government",
                                     "total", "commercial_pct"])
    df = past.copy()
    df["sector"] = df["provider_type"].apply(_classify_sector)

    grouped = (
        df.groupby(["year", "sector"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    for col in ("Commercial", "Government"):
        if col not in grouped.columns:
            grouped[col] = 0
    grouped["total"] = grouped["Commercial"] + grouped["Government"]
    grouped["commercial_pct"] = (
        grouped["Commercial"] / grouped["total"] * 100
    ).round(1)
    return grouped.sort_values("year")


def newspace_growth(past: pd.DataFrame) -> dict:
    """Commercial share evolution: earliest vs latest year in data."""
    by_year = sector_by_year(past)
    if by_year.empty:
        return {"first_year": None, "first_pct": 0.0,
                "last_year": None, "last_pct": 0.0, "delta": 0.0}
    first, last = by_year.iloc[0], by_year.iloc[-1]
    return {
        "first_year": int(first["year"]),
        "first_pct": float(first["commercial_pct"]),
        "last_year": int(last["year"]),
        "last_pct": float(last["commercial_pct"]),
        "delta": round(float(last["commercial_pct"]) - float(first["commercial_pct"]), 1),
    }


def provider_diversity_by_year(past: pd.DataFrame) -> pd.DataFrame:
    """Distinct active providers per year, split by sector."""
    if past.empty:
        return pd.DataFrame(columns=["year", "sector", "unique_providers"])
    df = past.copy()
    df["sector"] = df["provider_type"].apply(_classify_sector)
    return (
        df.groupby(["year", "sector"])["provider_name"]
        .nunique()
        .reset_index(name="unique_providers")
        .sort_values(["year", "sector"])
    )


# ---------------------------------------------------------------------------
# 7. Missions and orbits
# ---------------------------------------------------------------------------
DEEP_SPACE_KEYWORDS = (
    "lunar", "moon", "mars", "heliocentric", "interplanetary",
    "asteroid", "jupiter", "saturn", "venus", "mercury", "comet",
    "l1", "l2", "trans-lunar",
)


def normalize_orbit(orbit) -> str:
    """Group raw orbit names into analytical categories."""
    if not orbit or pd.isna(orbit):
        return "Unknown"
    o = str(orbit).lower().strip()
    # Deep space first so "Lunar Orbit" doesn't fall into Other
    for kw in DEEP_SPACE_KEYWORDS:
        if kw in o:
            return "Beyond Earth"
    if "suborbital" in o:
        return "Suborbital"
    if "geostationary" in o or "geosynchronous" in o or "gto" in o or o == "geo":
        return "GEO / GTO"
    if "medium earth" in o or o == "meo":
        return "MEO"
    if ("low earth" in o or o == "leo" or "sun-synchronous" in o
            or "sso" in o or "polar" in o or "iss" in o or "space station" in o):
        return "LEO"
    if "molniya" in o or "elliptical" in o or "highly elliptical" in o:
        return "HEO"
    return "Other"


def orbit_distribution(past: pd.DataFrame) -> pd.DataFrame:
    """Total launches per orbit category."""
    if past.empty:
        return pd.DataFrame(columns=["orbit_category", "count", "pct"])
    df = past.copy()
    df["orbit_category"] = df["mission_orbit"].apply(normalize_orbit)
    total = len(df)
    out = (
        df.groupby("orbit_category")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    out["pct"] = (out["count"] / total * 100).round(1)
    return out


def orbit_evolution(past: pd.DataFrame) -> pd.DataFrame:
    """Yearly launches per orbit category."""
    if past.empty:
        return pd.DataFrame(columns=["year", "orbit_category", "count"])
    df = past.copy()
    df["orbit_category"] = df["mission_orbit"].apply(normalize_orbit)
    return (
        df.groupby(["year", "orbit_category"])
        .size()
        .reset_index(name="count")
        .sort_values(["year", "orbit_category"])
    )


def mission_type_distribution(past: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top N mission types by launch count."""
    if past.empty:
        return pd.DataFrame(columns=["mission_type", "count"])
    return (
        past.dropna(subset=["mission_type"])
        .groupby("mission_type")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(n)
    )


def deep_space_missions(past: pd.DataFrame) -> pd.DataFrame:
    """Return missions that go beyond Earth orbit, sorted by date descending."""
    if past.empty:
        return pd.DataFrame()

    df = past.copy()
    orbit_lower = df["mission_orbit"].fillna("").str.lower()
    name_lower = df["launch_name"].fillna("").str.lower()

    mask = pd.Series(False, index=df.index)
    for kw in DEEP_SPACE_KEYWORDS:
        mask = mask | orbit_lower.str.contains(kw, regex=False)
        mask = mask | name_lower.str.contains(kw, regex=False)

    if "mission_type" in df.columns:
        mask = mask | (df["mission_type"].fillna("") == "Planetary Science")

    result = df[mask].copy()
    if result.empty:
        return result

    cols = ["net", "launch_name", "provider_name", "rocket_name", "mission_orbit", "mission_type"]
    for extra in ("rocket_fullname", "mission_description", "provider_logo_url", "provider_country", "pad_location", "pad_name"):
        if extra in result.columns and extra not in cols:
            cols.append(extra)
    return result[cols].sort_values("net", ascending=False).reset_index(drop=True)


def leo_dominance_headline(past: pd.DataFrame) -> tuple[float, int]:
    """Return (pct_leo, year) for the latest year in data."""
    if past.empty:
        return 0.0, 0
    latest_year = int(past["year"].max())
    year_df = past[past["year"] == latest_year].copy()
    year_df["orbit_category"] = year_df["mission_orbit"].apply(normalize_orbit)
    leo = (year_df["orbit_category"] == "LEO").sum()
    total = len(year_df)
    pct = (leo / total * 100) if total else 0.0
    return round(pct, 1), latest_year


# ---------------------------------------------------------------------------
# 8. Reliability scatter (success rate vs total launches)
# ---------------------------------------------------------------------------
_SUCCESS_STATUSES = {"Launch Successful", "Success"}
_CONCLUDED_STATUSES = _SUCCESS_STATUSES | {"Launch Failure", "Failure", "Partial Failure"}


def _entity_columns(df: pd.DataFrame, by: str) -> tuple[pd.Series, pd.Series]:
    """Return (name, color_group) series for the given grouping key. NaN names are kept as NaN so callers can drop them."""
    by_country = df["provider_country"].map(COUNTRY_GROUPS).fillna("Other")
    if by == "rocket":
        return df["rocket_name"], by_country
    if by == "family":
        return df["rocket_family"], by_country
    if by == "provider":
        return df["provider_name"], by_country
    if by == "pad":
        return df["pad_name"], df["pad_country"].map(COUNTRY_GROUPS).fillna("Other")
    if by == "mission_type":
        return df["mission_type"], by_country
    # country
    name = by_country
    return name, name


def reliability_by_category(past: pd.DataFrame, by: str = "provider") -> pd.DataFrame:
    """Return success-rate scatter data per entity (provider / rocket / pad / country)."""
    if past.empty:
        return pd.DataFrame(columns=["name", "total", "successes", "success_rate", "color_group"])

    df = past[past["status_name"].isin(_CONCLUDED_STATUSES)].copy()
    if df.empty:
        return pd.DataFrame(columns=["name", "total", "successes", "success_rate", "color_group"])

    df["is_success"] = df["status_name"].isin(_SUCCESS_STATUSES)
    df["name"], df["color_group"] = _entity_columns(df, by)
    df = df.dropna(subset=["name"])

    grouped = (
        df.groupby("name")
        .agg(total=("is_success", "count"), successes=("is_success", "sum"),
             color_group=("color_group", "first"))
        .reset_index()
    )
    grouped["success_rate"] = (grouped["successes"] / grouped["total"] * 100).round(1)
    return grouped.sort_values("total", ascending=False)


# ---------------------------------------------------------------------------
# 9. Launches by category (rocket / provider / country / pad)
# ---------------------------------------------------------------------------
def launches_by_category(past: pd.DataFrame, by: str = "rocket", n: int = 20) -> pd.DataFrame:
    """Return top N launch counts grouped by rocket, provider, country/region, or pad."""
    if past.empty:
        return pd.DataFrame(columns=["category", "count"])

    name_col, _ = _entity_columns(past, by)
    return (
        past.assign(category=name_col)
        .dropna(subset=["category"])
        .groupby("category")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(n)
    )


# ---------------------------------------------------------------------------
# 9. Calendar / weekly view
# ---------------------------------------------------------------------------

def upcoming_by_week(upcoming: pd.DataFrame) -> list[dict]:
    """
    Group upcoming launches by ISO week, returning a list of dicts
    suitable for rendering sequentially.
    """
    if upcoming.empty:
        return []

    df = upcoming.copy().sort_values("net")
    df["week_start"] = df["net"].apply(
        lambda d: (d - pd.Timedelta(days=d.weekday())).normalize()
    )

    weeks = []
    for week_start, group in df.groupby("week_start"):
        week_end = week_start + pd.Timedelta(days=6)
        weeks.append({
            "start": week_start,
            "end": week_end,
            "count": len(group),
            "launches": group,
        })
    return weeks


# ---------------------------------------------------------------------------
# 10. Overview headline stats
# ---------------------------------------------------------------------------
def overview_headline_stats(past: pd.DataFrame) -> dict:
    """Return pace and record stats for the overview tab headline."""
    if past.empty:
        return {}
    now = pd.Timestamp.now(tz="UTC")
    cur_year = now.year
    by_year = past.groupby("year").size()

    this_year_count = int(by_year.get(cur_year, 0))
    last_year_count = int(by_year.get(cur_year - 1, 0))

    day_of_year = now.timetuple().tm_yday
    projected = int(round(this_year_count / day_of_year * 365)) if day_of_year > 0 and this_year_count > 0 else this_year_count

    yoy_delta_pct = round((projected - last_year_count) / last_year_count * 100, 1) if last_year_count > 0 else None

    record_year = int(by_year.idxmax())
    record_count = int(by_year.max())

    return {
        "cur_year": cur_year,
        "this_year_count": this_year_count,
        "last_year": cur_year - 1,
        "last_year_count": last_year_count,
        "projected": projected,
        "yoy_delta_pct": yoy_delta_pct,
        "record_year": record_year,
        "record_count": record_count,
    }


def monthly_seasonality(past: pd.DataFrame) -> pd.DataFrame:
    """Average launches per calendar month across all years in the data."""
    if past.empty:
        return pd.DataFrame(columns=["month_num", "avg_launches"])
    df = past.copy()
    df["month_num"] = df["net"].dt.month
    by_month_year = df.groupby(["year", "month_num"]).size().reset_index(name="count")
    avg = (
        by_month_year.groupby("month_num")["count"]
        .mean()
        .round(1)
        .reset_index()
        .rename(columns={"count": "avg_launches"})
    )
    return avg.sort_values("month_num").reset_index(drop=True)


def success_rate_by_year(past: pd.DataFrame, min_launches: int = 3) -> pd.DataFrame:
    """Yearly success rate for concluded launches."""
    if past.empty:
        return pd.DataFrame(columns=["year", "success_rate", "total"])
    concluded = past[past["status_name"].isin(_CONCLUDED_STATUSES)].copy()
    if concluded.empty:
        return pd.DataFrame(columns=["year", "success_rate", "total"])
    concluded["is_success"] = concluded["status_name"].isin(_SUCCESS_STATUSES)
    result = (
        concluded.groupby("year")
        .agg(total=("is_success", "count"), successes=("is_success", "sum"))
        .reset_index()
    )
    result["success_rate"] = (result["successes"] / result["total"] * 100).round(1)
    return result[result["total"] >= min_launches].sort_values("year")


# ---------------------------------------------------------------------------
# 11. Explorer — flexible aggregations
# ---------------------------------------------------------------------------
_EXPLORER_COL = {
    "rocket": "rocket_name",
    "family": "rocket_family",
    "provider": "provider_name",
    "country": None,        # handled via COUNTRY_GROUPS
    "pad": "pad_name",
    "mission_type": "mission_type",
    "sector": "provider_type",
    "era": None,            # derived from year
    "year": "year",
    "quarter": None,        # derived from net
    "month": "month",
}


_NEW_SPACE_YEAR = 2010


def _explorer_group(df: pd.DataFrame, group_by: str) -> pd.Series:
    if group_by == "country":
        return df["provider_country"].map(COUNTRY_GROUPS).fillna("Other")
    if group_by == "quarter":
        return df["net"].dt.tz_convert(None).dt.to_period("Q").astype(str)
    if group_by == "year":
        return df["year"].astype(str)
    if group_by == "era":
        return df["year"].apply(lambda y: "New Space" if y >= _NEW_SPACE_YEAR else "Classic Space")
    col = _EXPLORER_COL.get(group_by, group_by)
    return df[col].fillna("Unknown")


def _success_rate_agg(grp: pd.DataFrame) -> float:
    concluded = grp["status_name"].isin(_CONCLUDED_STATUSES).sum()
    successes = grp["status_name"].isin(_SUCCESS_STATUSES).sum()
    return round(successes / concluded * 100, 1) if concluded else float("nan")


def explorer_group_count(past: pd.DataFrame, group_by: str) -> int:
    """Return the number of unique groups for the given grouping dimension."""
    if past.empty:
        return 1
    return int(_explorer_group(past, group_by).nunique())


def explorer_bar(past: pd.DataFrame, group_by: str = "provider", metric: str = "count",
                 top_n: int = 15, color_by: str | None = None, select_bottom: bool = False) -> pd.DataFrame:
    """Bar chart data: top_n groups by count or success rate.

    When color_by is set (and differs from group_by), returns columns [group, color, value]
    for a stacked/grouped bar; otherwise returns [group, value].
    """
    if past.empty:
        return pd.DataFrame(columns=["group", "value"])
    df = past.copy()
    df["group"] = _explorer_group(df, group_by)

    use_color = color_by is not None and color_by != group_by
    if use_color:
        df["color"] = _explorer_group(df, color_by)

    # Determine top/bottom N primary groups by total count
    top_groups = (
        df.groupby("group").size()
        .sort_values(ascending=select_bottom)
        .head(top_n)
        .index.tolist()
    )
    df = df[df["group"].isin(top_groups)]

    if not use_color:
        if metric == "count":
            result = (
                df.groupby("group").size()
                .reset_index(name="value")
                .sort_values("value", ascending=select_bottom)
            )
        else:
            result = (
                df.groupby("group")
                .apply(_success_rate_agg)
                .reset_index(name="value")
                .dropna(subset=["value"])
                .sort_values("value", ascending=select_bottom)
            )
        return result.reset_index(drop=True)
    else:
        if metric == "count":
            result = df.groupby(["group", "color"]).size().reset_index(name="value")
        else:
            result = (
                df.groupby(["group", "color"])
                .apply(_success_rate_agg)
                .reset_index(name="value")
                .dropna(subset=["value"])
            )
        return result.reset_index(drop=True)


def explorer_line(past: pd.DataFrame, group_by: str = "provider", metric: str = "count",
                  time_grain: str = "year", top_n: int = 8, select_bottom: bool = False) -> pd.DataFrame:
    """Line chart data: time × group_by. Returns columns [time, group, value]."""
    if past.empty:
        return pd.DataFrame(columns=["time", "group", "value"])
    df = past.copy()
    df["group"] = _explorer_group(df, group_by)
    if time_grain == "year":
        df["time"] = df["year"].astype(str)
    elif time_grain == "quarter":
        df["time"] = df["net"].dt.tz_convert(None).dt.to_period("Q").astype(str)
    else:  # month
        df["time"] = df["net"].dt.tz_convert(None).dt.to_period("M").astype(str)

    top_groups = (
        df.groupby("group").size()
        .sort_values(ascending=select_bottom)
        .head(top_n)
        .index.tolist()
    )
    df = df[df["group"].isin(top_groups)]

    if metric == "count":
        result = df.groupby(["time", "group"]).size().reset_index(name="value")
    else:
        result = (
            df.groupby(["time", "group"])
            .apply(_success_rate_agg)
            .reset_index(name="value")
        )
    result.columns = ["time", "group", "value"]
    return result.sort_values("time")


def explorer_scatter(past: pd.DataFrame, group_by: str = "provider", min_launches: int = 5,
                     color_by: str | None = None) -> pd.DataFrame:
    """Scatter data: launches (x) vs success rate (y) per group.
    When color_by is set, adds a 'color' column (dominant value of that dimension within each group).
    Columns: [group, launches, success_rate] or [group, color, launches, success_rate].
    """
    if past.empty:
        return pd.DataFrame(columns=["group", "launches", "success_rate"])
    df = past.copy()
    df["group"] = _explorer_group(df, group_by)
    use_color = color_by is not None and color_by != group_by
    if use_color:
        df["color"] = _explorer_group(df, color_by)
    records = []
    for name, grp in df.groupby("group"):
        count = len(grp)
        if count < min_launches:
            continue
        rate = _success_rate_agg(grp)
        if not pd.isna(rate):
            rec = {"group": name, "launches": count, "success_rate": rate}
            if use_color:
                mode_vals = grp["color"].mode()
                rec["color"] = mode_vals.iloc[0] if len(mode_vals) > 0 else "Unknown"
            records.append(rec)
    return pd.DataFrame(records).sort_values("launches", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 12. Launch density with forecast
# ---------------------------------------------------------------------------
def launches_by_year_with_forecast(past: pd.DataFrame) -> pd.DataFrame:
    """Annual launch counts with projected totals for the current and next year.

    Returns a 'type' column: 'actual' | 'current_projected' | 'forecast'.
    current_projected: regression estimate for the in-progress year (shown behind the partial actual bar).
    forecast: estimate for next calendar year.
    """
    if past.empty:
        return pd.DataFrame(columns=["year", "count", "type"])

    now = pd.Timestamp.now(tz="UTC")
    cur_year = now.year
    by_year = past.groupby("year").size().reset_index(name="count").sort_values("year")
    by_year["type"] = "actual"

    complete = by_year[by_year["year"] < cur_year].tail(5)
    if len(complete) >= 2:
        x = complete["year"].astype(float)
        y = complete["count"].astype(float)
        n = float(len(x))
        slope = (n * (x * y).sum() - x.sum() * y.sum()) / (n * (x ** 2).sum() - x.sum() ** 2)
        intercept = y.mean() - slope * x.mean()

        extra = []
        if cur_year in by_year["year"].values:
            cur_proj = max(0, int(round(float(slope * cur_year + intercept))))
            extra.append({"year": cur_year, "count": cur_proj, "type": "current_projected"})

        latest = int(by_year["year"].max())
        for next_year in (latest + 1, latest + 2):
            proj = max(0, int(round(float(slope * next_year + intercept))))
            extra.append({"year": next_year, "count": proj, "type": "forecast"})

        by_year = pd.concat([by_year, pd.DataFrame(extra)], ignore_index=True)
    return by_year


# ---------------------------------------------------------------------------
# 13. Rocket families — yearly activity
# ---------------------------------------------------------------------------
def rocket_family_by_year(past: pd.DataFrame, min_total: int = 5, top_n: int = 12) -> pd.DataFrame:
    """Yearly launch counts for the top N most active rocket families."""
    if past.empty:
        return pd.DataFrame(columns=["year", "family", "count"])
    df = past.dropna(subset=["rocket_family"]).copy()
    totals = df.groupby("rocket_family").size().sort_values(ascending=False)
    top_families = totals[totals >= min_total].head(top_n).index.tolist()
    df = df[df["rocket_family"].isin(top_families)]
    return (
        df.groupby(["year", "rocket_family"])
        .size()
        .reset_index(name="count")
        .rename(columns={"rocket_family": "family"})
        .sort_values(["year", "family"])
    )



# ---------------------------------------------------------------------------
# 14. Falcon 9 turnaround time
# ---------------------------------------------------------------------------
def falcon9_turnaround(past: pd.DataFrame) -> pd.DataFrame:
    """Days between consecutive Falcon 9 launches as a reusability metric."""
    if past.empty:
        return pd.DataFrame(columns=["net", "days", "launch_name"])

    f9 = (
        past[past["rocket_name"].fillna("").str.contains("Falcon 9", case=False)]
        .copy().sort_values("net").reset_index(drop=True)
    )
    if len(f9) < 2:
        return pd.DataFrame(columns=["net", "days", "launch_name"])

    f9["days"] = (f9["net"].diff().dt.total_seconds() / 86400).round(1)
    return f9[["net", "days", "launch_name"]].dropna(subset=["days"]).reset_index(drop=True)

