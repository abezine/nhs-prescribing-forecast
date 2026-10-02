import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def toy_df() -> pd.DataFrame:
    """Two series, 40 months, seasonal + trend."""
    rng = np.random.default_rng(0)
    months = pd.date_range("2021-01-01", periods=40, freq="MS")
    rows = []
    for sid, region, chap, base in [("Y56_05", "Y56", "05", 1000), ("Y58_02", "Y58", "02", 5000)]:
        for i, m in enumerate(months):
            y = base * (1 + 0.3 * np.cos(2 * np.pi * (m.month - 1) / 12)) * (1 + 0.01 * i) + rng.normal(0, 10)
            rows.append(dict(series_id=sid, month_start=m, region_code=region, bnf_chapter_code=chap,
                             bnf_chapter_name="x", region_name="x", y=y, is_missing=False))
    return pd.DataFrame(rows)
