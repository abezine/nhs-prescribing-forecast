import pandas as pd

from rxforecast.baselines import naive_last, seasonal_naive


def test_naive_last_returns_origin_value(toy_df):
    origin = pd.Timestamp("2023-06-01")
    got = naive_last(toy_df, origin, h=2)
    expected = toy_df[toy_df.month_start == origin].set_index("series_id")["y"]
    pd.testing.assert_series_equal(got, expected)


def test_seasonal_naive_looks_back_one_year_from_target(toy_df):
    origin = pd.Timestamp("2023-06-01")
    got = seasonal_naive(toy_df, origin, h=3)          # target 2023-09 -> reference 2022-09
    expected = toy_df[toy_df.month_start == "2022-09-01"].set_index("series_id")["y"]
    pd.testing.assert_series_equal(got, expected)
