import numpy as np
import pandas as pd


def mae(y, yhat) -> float:
    return float(np.mean(np.abs(np.asarray(y, float) - np.asarray(yhat, float))))


def wape(y, yhat) -> float:
    """Weighted absolute percentage error: sum|e| / sum|y|. Robust to small series."""
    y, yhat = np.asarray(y, float), np.asarray(yhat, float)
    return float(np.sum(np.abs(y - yhat)) / np.sum(np.abs(y)))


def seasonal_scale(history: pd.DataFrame, season: int = 12) -> pd.Series:
    """Per-series in-sample MAE of the seasonal naive forecast (MASE denominator).
    Computed on training history only, so it never sees the test window."""
    h = history.sort_values(["series_id", "month_start"])
    diff = h.groupby("series_id")["y"].diff(season).abs()
    return diff.groupby(h["series_id"]).mean()


def mase(y, yhat, scale) -> float:
    y, yhat, scale = (np.asarray(a, float) for a in (y, yhat, scale))
    return float(np.mean(np.abs(y - yhat) / scale))


def summarise(pred: pd.DataFrame) -> dict:
    """pred needs columns y, yhat, scale."""
    return {
        "MAE": mae(pred["y"], pred["yhat"]),
        "WAPE": wape(pred["y"], pred["yhat"]),
        "MASE": mase(pred["y"], pred["yhat"], pred["scale"]),
        "n": int(len(pred)),
    }
