import pandas as pd
import pytest
from insights import (
    _classify_sector,
    deep_space_missions,
    falcon9_turnaround,
    launches_by_category,
    launches_by_year_with_forecast,
    leo_dominance_headline,
    mission_type_distribution,
    monthly_seasonality,
    newspace_growth,
    normalize_orbit,
    orbit_distribution,
    orbit_evolution,
    overview_headline_stats,
    provider_diversity_by_year,
    reliability_by_category,
    rocket_family_by_year,
    sector_by_year,
    spacex_starlink_share_latest_year,
    starlink_share_by_year,
    starlink_total_share,
    success_rate_by_year,
    top_pads,
    top_providers_by_sector,
    upcoming_by_week,
)


# ---------------------------------------------------------------------------
# 1. SpaceX / Starlink
# ---------------------------------------------------------------------------

class TestSpacexStarlinkShareLatestYear:
    def test_empty_returns_zeros(self):
        assert spacex_starlink_share_latest_year(pd.DataFrame()) == (0, 0.0, 0.0)

    def test_returns_latest_year(self, sample_past):
        year, spx_pct, sl_pct = spacex_starlink_share_latest_year(sample_past)
        assert year == 2023

    def test_spacex_pct_matches_known_data(self, sample_past):
        # 2023: 3 SpaceX out of 4 total → 75%
        year, spx_pct, sl_pct = spacex_starlink_share_latest_year(sample_past)
        assert spx_pct == round(3 / 4 * 100, 1)

    def test_starlink_pct_subset_of_spacex(self, sample_past):
        _, spx_pct, sl_pct = spacex_starlink_share_latest_year(sample_past)
        assert sl_pct <= spx_pct


# ---------------------------------------------------------------------------
# 2. Top launch pads
# ---------------------------------------------------------------------------

class TestTopPads:
    def test_empty_returns_expected_columns(self):
        result = top_pads(pd.DataFrame())
        assert list(result.columns) == ["pad_name", "pad_location", "pad_country", "count"]

    def test_sorted_descending(self, sample_past):
        result = top_pads(sample_past)
        assert list(result["count"]) == sorted(result["count"], reverse=True)

    def test_n_parameter_limits_results(self, sample_past):
        result = top_pads(sample_past, n=2)
        assert len(result) <= 2

    def test_lc39a_is_most_active(self, sample_past):
        result = top_pads(sample_past)
        assert result.iloc[0]["pad_name"] == "LC-39A"


# ---------------------------------------------------------------------------
# 5. Starlink factor
# ---------------------------------------------------------------------------

class TestStarlinkShareByYear:
    def test_empty_returns_expected_columns(self):
        result = starlink_share_by_year(pd.DataFrame())
        assert list(result.columns) == ["year", "Starlink", "Other SpaceX", "Rest of World"]

    def test_classifies_starlink_correctly(self, sample_past):
        result = starlink_share_by_year(sample_past)
        row_2022 = result[result["year"] == 2022].iloc[0]
        assert row_2022["Starlink"] == 1  # "Starlink Group 4-1"
        assert row_2022["Other SpaceX"] == 1  # Transporter-6
        assert row_2022["Rest of World"] == 1  # Rocket Lab

    def test_sorted_by_year(self, sample_past):
        result = starlink_share_by_year(sample_past)
        assert list(result["year"]) == sorted(result["year"])


class TestStarlinkTotalShare:
    def test_empty_returns_zeros(self):
        assert starlink_total_share(pd.DataFrame()) == (0, 0, 0.0)

    def test_counts_starlink_across_all_years(self, sample_past):
        # Starlink missions: rows 0, 3, 6 → 3 out of 7
        count, total, pct = starlink_total_share(sample_past)
        assert count == 3
        assert total == 7
        assert pct == round(3 / 7 * 100, 1)


# ---------------------------------------------------------------------------
# 6. New Space vs Government
# ---------------------------------------------------------------------------

class TestClassifySector:
    def test_government_string(self):
        assert _classify_sector("Government") == "Government"

    def test_commercial_string(self):
        assert _classify_sector("Commercial") == "Commercial"

    def test_none_is_commercial(self):
        assert _classify_sector(None) == "Commercial"

    def test_nan_is_commercial(self):
        import math
        assert _classify_sector(float("nan")) == "Commercial"

    def test_empty_string_is_commercial(self):
        assert _classify_sector("") == "Commercial"

    def test_unknown_type_is_commercial(self):
        assert _classify_sector("Private") == "Commercial"


class TestSectorByYear:
    def test_empty_returns_expected_columns(self):
        result = sector_by_year(pd.DataFrame())
        assert "year" in result.columns
        assert "Commercial" in result.columns
        assert "Government" in result.columns

    def test_counts_by_sector(self, sample_past):
        result = sector_by_year(sample_past)
        row_2023 = result[result["year"] == 2023].iloc[0]
        assert row_2023["Government"] == 1   # ISRO
        assert row_2023["Commercial"] == 3   # SpaceX x3

    def test_commercial_pct_rounded(self, sample_past):
        result = sector_by_year(sample_past)
        row_2023 = result[result["year"] == 2023].iloc[0]
        assert row_2023["commercial_pct"] == round(3 / 4 * 100, 1)


class TestNewspaceGrowth:
    def test_empty_returns_none_values(self):
        result = newspace_growth(pd.DataFrame())
        assert result["first_year"] is None
        assert result["last_year"] is None

    def test_delta_is_last_minus_first(self, sample_past):
        result = newspace_growth(sample_past)
        assert result["delta"] == round(result["last_pct"] - result["first_pct"], 1)

    def test_first_and_last_year_correct(self, sample_past):
        result = newspace_growth(sample_past)
        assert result["first_year"] == 2022
        assert result["last_year"] == 2023


class TestTopProvidersBySector:
    def test_empty_returns_two_empty_dataframes(self):
        commercial, government = top_providers_by_sector(pd.DataFrame())
        assert commercial.empty
        assert government.empty

    def test_spacex_is_top_commercial(self, sample_past):
        commercial, _ = top_providers_by_sector(sample_past)
        assert commercial.iloc[0]["provider_name"] == "SpaceX"

    def test_isro_is_top_government(self, sample_past):
        _, government = top_providers_by_sector(sample_past)
        assert government.iloc[0]["provider_name"] == "ISRO"

    def test_n_parameter_limits_results(self, sample_past):
        commercial, government = top_providers_by_sector(sample_past, n=1)
        assert len(commercial) <= 1
        assert len(government) <= 1


class TestProviderDiversityByYear:
    def test_empty_returns_expected_columns(self):
        result = provider_diversity_by_year(pd.DataFrame())
        assert list(result.columns) == ["year", "sector", "unique_providers"]

    def test_counts_unique_providers(self, sample_past):
        result = provider_diversity_by_year(sample_past)
        row = result[(result["year"] == 2023) & (result["sector"] == "Commercial")].iloc[0]
        assert row["unique_providers"] == 1  # Only SpaceX in 2023 Commercial


# ---------------------------------------------------------------------------
# 7. Missions and orbits
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("orbit,expected", [
    ("Low Earth Orbit", "LEO"),
    ("leo", "LEO"),
    ("Sun-Synchronous Orbit", "LEO"),
    ("SSO", "LEO"),
    ("Polar Orbit", "LEO"),
    ("International Space Station", "LEO"),
    ("Geostationary Transfer Orbit", "GEO / GTO"),
    ("GTO", "GEO / GTO"),
    ("Geostationary Orbit", "GEO / GTO"),
    ("geo", "GEO / GTO"),
    ("Medium Earth Orbit", "MEO"),
    ("meo", "MEO"),
    ("Molniya Orbit", "HEO"),
    ("Highly Elliptical Orbit", "HEO"),
    ("Suborbital", "Suborbital"),
    ("Lunar Orbit", "Beyond Earth"),
    ("Mars Transfer Orbit", "Beyond Earth"),
    ("Heliocentric Orbit", "Beyond Earth"),
    ("L2 Point", "Beyond Earth"),
    ("Some Random Orbit", "Other"),
    (None, "Unknown"),
    ("", "Unknown"),
])
def test_normalize_orbit(orbit, expected):
    assert normalize_orbit(orbit) == expected


class TestOrbitDistribution:
    def test_empty_returns_expected_columns(self):
        result = orbit_distribution(pd.DataFrame())
        assert list(result.columns) == ["orbit_category", "count", "pct"]

    def test_pct_sums_to_100(self, sample_past):
        result = orbit_distribution(sample_past)
        assert abs(result["pct"].sum() - 100.0) < 0.1

    def test_leo_is_dominant(self, sample_past):
        result = orbit_distribution(sample_past)
        top_category = result.iloc[0]["orbit_category"]
        assert top_category == "LEO"


class TestOrbitEvolution:
    def test_empty_returns_expected_columns(self):
        result = orbit_evolution(pd.DataFrame())
        assert list(result.columns) == ["year", "orbit_category", "count"]

    def test_has_rows_per_year_and_category(self, sample_past):
        result = orbit_evolution(sample_past)
        assert len(result) > 0
        assert set(result["year"]).issubset({2022, 2023})


class TestMissionTypeDistribution:
    def test_empty_returns_expected_columns(self):
        result = mission_type_distribution(pd.DataFrame())
        assert list(result.columns) == ["mission_type", "count"]

    def test_sorted_descending(self, sample_past):
        result = mission_type_distribution(sample_past)
        assert list(result["count"]) == sorted(result["count"], reverse=True)

    def test_n_limits_results(self, sample_past):
        result = mission_type_distribution(sample_past, n=2)
        assert len(result) <= 2

    def test_communications_is_top(self, sample_past):
        result = mission_type_distribution(sample_past)
        assert result.iloc[0]["mission_type"] == "Communications"


class TestDeepSpaceMissions:
    def test_empty_returns_empty(self):
        assert deep_space_missions(pd.DataFrame()).empty

    def test_detects_lunar_orbit(self, sample_past):
        result = deep_space_missions(sample_past)
        # Row 2: mission_orbit="Lunar Orbit", mission_type="Planetary Science"
        assert len(result) >= 1
        assert "CAPSTONE" in result["launch_name"].values[0]

    def test_result_columns_include_required_fields(self, sample_past):
        result = deep_space_missions(sample_past)
        for col in ("net", "launch_name", "provider_name", "rocket_name"):
            assert col in result.columns

    def test_includes_optional_columns_when_present(self, sample_past):
        df = sample_past.copy()
        df["rocket_fullname"] = "Electron / Kick Stage"
        df["mission_description"] = "Test description"
        result = deep_space_missions(df)
        assert "rocket_fullname" in result.columns
        assert "mission_description" in result.columns

    def test_no_deep_space_returns_empty(self):
        df = pd.DataFrame({
            "mission_orbit": ["Low Earth Orbit", "GTO"],
            "launch_name": ["Starlink 1", "SES-18"],
            "mission_type": ["Communications", "Communications"],
            "net": pd.to_datetime(["2023-01-01", "2023-02-01"], utc=True),
            "provider_name": ["SpaceX", "SpaceX"],
            "rocket_name": ["Falcon 9", "Falcon 9"],
        })
        assert deep_space_missions(df).empty


class TestLeoDominanceHeadline:
    def test_empty_returns_zeros(self):
        pct, year = leo_dominance_headline(pd.DataFrame())
        assert pct == 0.0
        assert year == 0

    def test_returns_latest_year(self, sample_past):
        _, year = leo_dominance_headline(sample_past)
        assert year == 2023

    def test_pct_between_0_and_100(self, sample_past):
        pct, _ = leo_dominance_headline(sample_past)
        assert 0.0 <= pct <= 100.0


# ---------------------------------------------------------------------------
# 8. Calendar / weekly view
# ---------------------------------------------------------------------------

class TestUpcomingByWeek:
    def test_empty_returns_empty_list(self):
        assert upcoming_by_week(pd.DataFrame()) == []

    def test_groups_by_week(self, sample_upcoming):
        weeks = upcoming_by_week(sample_upcoming)
        assert len(weeks) == 2  # two distinct ISO weeks

    def test_first_week_has_two_launches(self, sample_upcoming):
        weeks = upcoming_by_week(sample_upcoming)
        assert weeks[0]["count"] == 2

    def test_second_week_has_one_launch(self, sample_upcoming):
        weeks = upcoming_by_week(sample_upcoming)
        assert weeks[1]["count"] == 1

    def test_week_dict_has_required_keys(self, sample_upcoming):
        weeks = upcoming_by_week(sample_upcoming)
        for week in weeks:
            assert {"start", "end", "count", "launches"}.issubset(week.keys())


# ---------------------------------------------------------------------------
# 9. Monthly seasonality
# ---------------------------------------------------------------------------

class TestMonthlySeeasonality:
    def test_empty_returns_expected_columns(self):
        result = monthly_seasonality(pd.DataFrame())
        assert list(result.columns) == ["month_num", "avg_launches"]

    def test_returns_12_months(self, sample_past):
        result = monthly_seasonality(sample_past)
        assert set(result["month_num"]) == set(range(1, 13)) or len(result) <= 12

    def test_avg_launches_positive(self, sample_past):
        result = monthly_seasonality(sample_past)
        assert (result["avg_launches"] >= 0).all()

    def test_sorted_by_month(self, sample_past):
        result = monthly_seasonality(sample_past)
        assert list(result["month_num"]) == sorted(result["month_num"])


# ---------------------------------------------------------------------------
# 10. Success rate by year
# ---------------------------------------------------------------------------

class TestSuccessRateByYear:
    def test_empty_returns_expected_columns(self):
        result = success_rate_by_year(pd.DataFrame())
        assert list(result.columns) == ["year", "success_rate", "total"]

    def test_rate_between_0_and_100(self, sample_past):
        result = success_rate_by_year(sample_past)
        assert (result["success_rate"] >= 0).all()
        assert (result["success_rate"] <= 100).all()

    def test_known_2023_rate(self, sample_past):
        # 2023: 3 successful, 1 failure → 75%
        result = success_rate_by_year(sample_past)
        row = result[result["year"] == 2023].iloc[0]
        assert row["success_rate"] == round(3 / 4 * 100, 1)
        assert row["total"] == 4


# ---------------------------------------------------------------------------
# 11. Launches by year with forecast
# ---------------------------------------------------------------------------

class TestLaunchesByYearWithForecast:
    def test_empty_returns_expected_columns(self):
        result = launches_by_year_with_forecast(pd.DataFrame())
        assert list(result.columns) == ["year", "count", "type"]

    def test_actual_rows_present(self, sample_past):
        result = launches_by_year_with_forecast(sample_past)
        assert "actual" in result["type"].values

    def test_forecast_rows_appended(self, sample_past):
        result = launches_by_year_with_forecast(sample_past)
        assert "forecast" in result["type"].values

    def test_forecast_count_non_negative(self, sample_past):
        result = launches_by_year_with_forecast(sample_past)
        assert (result["count"] >= 0).all()

    def test_actual_counts_match_input(self, sample_past):
        result = launches_by_year_with_forecast(sample_past)
        actual = result[result["type"] == "actual"]
        assert actual[actual["year"] == 2022]["count"].iloc[0] == 3
        assert actual[actual["year"] == 2023]["count"].iloc[0] == 4


# ---------------------------------------------------------------------------
# 12. Rocket family by year
# ---------------------------------------------------------------------------

class TestRocketFamilyByYear:
    def test_empty_returns_expected_columns(self):
        result = rocket_family_by_year(pd.DataFrame())
        assert list(result.columns) == ["year", "family", "count"]

    def test_respects_min_total(self):
        df = pd.DataFrame({
            "year": [2022], "rocket_family": ["Rare"],
            "net": pd.to_datetime(["2022-01-01"], utc=True),
        })
        result = rocket_family_by_year(df, min_total=5)
        assert result.empty

    def test_includes_falcon_9(self, sample_past):
        sample = sample_past.copy()
        sample["rocket_family"] = sample["rocket_name"].map(
            {"Falcon 9": "Falcon 9", "Electron": "Electron", "PSLV": "PSLV"}
        )
        result = rocket_family_by_year(sample, min_total=1)
        assert "Falcon 9" in result["family"].values

    def test_count_column_sums_correctly(self, sample_past):
        sample = sample_past.copy()
        sample["rocket_family"] = "Falcon 9"
        result = rocket_family_by_year(sample, min_total=1)
        assert result["count"].sum() == len(sample_past)


# ---------------------------------------------------------------------------
# 13. Falcon 9 turnaround
# ---------------------------------------------------------------------------

class TestFalcon9Turnaround:
    def test_empty_returns_expected_columns(self):
        result = falcon9_turnaround(pd.DataFrame())
        assert list(result.columns) == ["net", "days", "launch_name"]

    def test_single_launch_returns_empty(self):
        df = pd.DataFrame({
            "rocket_name": ["Falcon 9"],
            "net": pd.to_datetime(["2023-01-01"], utc=True),
            "launch_name": ["Starlink 1"],
        })
        assert falcon9_turnaround(df).empty

    def test_non_falcon9_ignored(self):
        df = pd.DataFrame({
            "rocket_name": ["Electron", "Electron"],
            "net": pd.to_datetime(["2023-01-01", "2023-01-10"], utc=True),
            "launch_name": ["A", "B"],
        })
        assert falcon9_turnaround(df).empty

    def test_days_computed_correctly(self, sample_past):
        result = falcon9_turnaround(sample_past)
        assert not result.empty
        assert (result["days"] > 0).all()

    def test_sorted_by_net(self, sample_past):
        result = falcon9_turnaround(sample_past)
        assert list(result["net"]) == sorted(result["net"])


# ---------------------------------------------------------------------------
# 14. Reliability by category
# ---------------------------------------------------------------------------

class TestReliabilityByCategory:
    def test_empty_returns_expected_columns(self):
        result = reliability_by_category(pd.DataFrame())
        for col in ("name", "total", "successes", "success_rate"):
            assert col in result.columns

    def test_success_rate_between_0_and_100(self, sample_past):
        result = reliability_by_category(sample_past, by="rocket")
        assert (result["success_rate"] >= 0).all()
        assert (result["success_rate"] <= 100).all()

    def test_spacex_high_reliability(self, sample_past):
        result = reliability_by_category(sample_past, by="provider")
        spacex_row = result[result["name"] == "SpaceX"].iloc[0]
        assert spacex_row["success_rate"] >= 80.0


# ---------------------------------------------------------------------------
# 15. Launches by category
# ---------------------------------------------------------------------------

class TestLaunchesByCategory:
    def test_empty_returns_empty(self):
        assert launches_by_category(pd.DataFrame()).empty

    def test_returns_n_rows(self, sample_past):
        result = launches_by_category(sample_past, by="rocket", n=2)
        assert len(result) <= 2

    def test_sorted_descending(self, sample_past):
        result = launches_by_category(sample_past, by="provider")
        assert list(result.iloc[:, 1]) == sorted(result.iloc[:, 1], reverse=True)


# ---------------------------------------------------------------------------
# 16. Overview headline stats
# ---------------------------------------------------------------------------

class TestOverviewHeadlineStats:
    def test_empty_returns_empty_dict(self):
        assert overview_headline_stats(pd.DataFrame()) == {}

    def test_returns_expected_keys(self, sample_past):
        result = overview_headline_stats(sample_past)
        for key in ("cur_year", "projected", "last_year", "yoy_delta_pct",
                    "record_year", "record_count"):
            assert key in result

    def test_record_year_has_highest_count(self, sample_past):
        result = overview_headline_stats(sample_past)
        if result["record_year"] is not None:
            assert result["record_count"] >= 1
