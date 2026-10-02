import numpy as np
import pandas as pd

from rxforecast.backtest import fold_origins, split
from rxforecast.features import FEATURES, build_frame


def test_features_do_not_change_when_future_changes(toy_df):
    """Corrupting data after the origin must not alter features at the origin."""
    origin = pd.Timestamp("2023-06-01")
    clean = build_frame(toy_df)
    corrupted = toy_df.copy()
    corrupted.loc[corrupted.month_start > origin, "y"] *= 100
    dirty = build_frame(corrupted)

    num = [f for f in FEATURES if f not in ("region_code", "bnf_chapter_code")]
    a = clean[clean.origin == origin].sort_values(["series_id", "h"])[num].to_numpy(float)
    b = dirty[dirty.origin == origin].sort_values(["series_id", "h"])[num].to_numpy(float)
    np.testing.assert_allclose(a, b)


def test_train_targets_never_after_origin(toy_df):
    frame = build_frame(toy_df)
    for origin in fold_origins(frame, n_folds=5):
        train, test = split(frame, origin)
        assert train["target_month"].max() <= origin
        assert (test["origin"] == origin).all()
        assert set(test["h"]) == {1, 2, 3}


def test_fold_origins_leave_room_for_full_horizon(toy_df):
    frame = build_frame(toy_df)
    last = toy_df.month_start.max()
    assert max(fold_origins(frame, n_folds=3)) == last - pd.DateOffset(months=3)
