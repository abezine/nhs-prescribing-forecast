"""Leakage-safe feature construction for direct multi-horizon forecasting.

Every row is (series, origin month t, horizon h). Features use only y at months <= t.
The target is y at month t+h. One model is trained across all horizons with h as a feature.
To keep series on a common scale, the model learns log(y[t+h] / level_t),
where level_t is the mean of the last 3 observed months.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import HORIZON, LAGS

CATEGORICAL = ["region_code", "bnf_chapter_code"]


def _wide(df: pd.DataFrame) -> pd.DataFrame:
    return df.pivot(index="month_start", columns="series_id", values="y").sort_index()


def build_frame(df: pd.DataFrame, horizon: int = HORIZON, include_future: bool = False) -> pd.DataFrame:
    """Return one row per (series, origin, h).

    include_future=True also emits origins whose target lies beyond the data
    (target NaN) so the final model can produce real forecasts.
    """
    wide = _wide(df)
    labels = df.drop_duplicates("series_id").set_index("series_id")[CATEGORICAL]
    log_y = np.log1p(wide)

    level = wide.rolling(3, min_periods=3).mean()
    log_level = np.log1p(level)

    base = {}
    for lag in LAGS:
        # log ratio of y[t-lag+1] to current level: shape of recent history
        base[f"lag_{lag}"] = log_y.shift(lag - 1) - log_level
    base["roll_mean_12"] = np.log1p(wide.rolling(12, min_periods=12).mean()) - log_level
    base["growth_3m"] = log_y - log_y.shift(3)
    base["growth_12m"] = log_y - log_y.shift(12)
    base["log_level"] = log_level

    frames = []
    for h in range(1, horizon + 1):
        target = wide.shift(-h)
        parts = {name: feat.stack(future_stack=True) for name, feat in base.items()}
        parts["y_target"] = target.stack(future_stack=True)
        parts["level"] = level.stack(future_stack=True)
        # seasonal anchor: same month last year relative to current level
        parts["seasonal_ref"] = (log_y.shift(12 - h) - log_level).stack(future_stack=True)
        f = pd.DataFrame(parts).reset_index().rename(columns={"month_start": "origin"})
        f["h"] = h
        f["target_month"] = f["origin"] + pd.DateOffset(months=h)
        frames.append(f)

    out = pd.concat(frames, ignore_index=True)
    out["target_month_of_year"] = out["target_month"].dt.month
    out = out.join(labels, on="series_id")
    for c in CATEGORICAL:
        out[c] = out[c].astype("category")

    out = out.dropna(subset=["level", "lag_12"])  # need a full year of history
    if not include_future:
        out = out.dropna(subset=["y_target"])
    out["log_ratio_target"] = np.log(out["y_target"] / out["level"])
    return out.sort_values(["origin", "series_id", "h"]).reset_index(drop=True)


FEATURES = (
    [f"lag_{l}" for l in LAGS]
    + ["roll_mean_12", "growth_3m", "growth_12m", "log_level", "seasonal_ref", "h", "target_month_of_year"]
    + CATEGORICAL
)
