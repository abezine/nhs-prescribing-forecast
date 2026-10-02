"""Baselines the model has to beat. Both use only information available at the origin."""
import pandas as pd


def naive_last(df: pd.DataFrame, origin: pd.Timestamp, h: int) -> pd.Series:
    """Forecast = last observed value at the origin."""
    last = df[df["month_start"] == origin].set_index("series_id")["y"]
    return last


def seasonal_naive(df: pd.DataFrame, origin: pd.Timestamp, h: int, season: int = 12) -> pd.Series:
    """Forecast = value in the same month one year before the target month."""
    ref_month = origin + pd.DateOffset(months=h - season)
    return df[df["month_start"] == ref_month].set_index("series_id")["y"]


BASELINES = {"naive_last": naive_last, "seasonal_naive": seasonal_naive}
