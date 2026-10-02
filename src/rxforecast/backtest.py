"""Rolling-origin backtest.

For each origin T (the last month we pretend to know):
  train = all (origin, h) rows whose *target month* is <= T   -> no future leakage
  test  = rows with origin == T, h = 1..HORIZON
The model and every baseline are scored on exactly the same test rows.
"""
from __future__ import annotations

import pandas as pd

from . import model as mdl
from .baselines import BASELINES
from .config import HORIZON, N_FOLDS, SEASON
from .metrics import seasonal_scale


def fold_origins(frame: pd.DataFrame, n_folds: int = N_FOLDS, horizon: int = HORIZON) -> list[pd.Timestamp]:
    last_month = frame["target_month"].max()
    max_origin = last_month - pd.DateOffset(months=horizon)
    origins = sorted(o for o in frame["origin"].unique() if o <= max_origin)
    return [pd.Timestamp(o) for o in origins[-n_folds:]]


def split(frame: pd.DataFrame, origin: pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = frame[frame["target_month"] <= origin]
    test = frame[frame["origin"] == origin]
    return train, test


def run(df: pd.DataFrame, frame: pd.DataFrame, n_folds: int = N_FOLDS) -> pd.DataFrame:
    rows = []
    for origin in fold_origins(frame, n_folds):
        train, test = split(frame, origin)
        assert train["target_month"].max() <= origin, "leakage: training target after origin"

        history = df[df["month_start"] <= origin]
        scale = seasonal_scale(history, SEASON)

        keys = test[["series_id", "origin", "h", "target_month", "y_target"]].rename(columns={"y_target": "y"})
        keys["scale"] = keys["series_id"].map(scale).to_numpy()

        fitted = mdl.fit(train)
        rows.append(keys.assign(model="hgb", yhat=mdl.predict(fitted, test)))

        for name, fn in BASELINES.items():
            preds = []
            for h in range(1, HORIZON + 1):
                sub = keys[keys["h"] == h]
                preds.append(sub.assign(model=name, yhat=sub["series_id"].map(fn(history, origin, h)).to_numpy()))
            rows.append(pd.concat(preds))

        print(f"  fold origin {origin:%Y-%m}: train rows {len(train):,}, test rows {len(test):,}")

    return pd.concat(rows, ignore_index=True)
