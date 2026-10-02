import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from .config import RANDOM_STATE
from .features import FEATURES


def make_model() -> HistGradientBoostingRegressor:
    return HistGradientBoostingRegressor(
        loss="absolute_error",        # optimise the error we report
        learning_rate=0.05,
        max_iter=400,
        max_leaf_nodes=15,
        min_samples_leaf=20,
        l2_regularization=1.0,
        categorical_features="from_dtype",
        random_state=RANDOM_STATE,
    )


def fit(train: pd.DataFrame) -> HistGradientBoostingRegressor:
    model = make_model()
    model.fit(train[FEATURES], train["log_ratio_target"])
    return model


def predict(model, frame: pd.DataFrame) -> np.ndarray:
    """Back-transform the log-ratio prediction to items."""
    return frame["level"].to_numpy() * np.exp(model.predict(frame[FEATURES]))
