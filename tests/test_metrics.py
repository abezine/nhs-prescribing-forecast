import pandas as pd
import pytest

from rxforecast.metrics import mae, mase, seasonal_scale, wape


def test_mae_and_wape():
    assert mae([10, 20], [12, 18]) == 2
    assert wape([10, 30], [12, 27]) == pytest.approx(5 / 40)


def test_mase_equals_one_for_seasonal_naive_quality_errors():
    assert mase([100, 100], [90, 110], [10, 10]) == 1


def test_seasonal_scale_uses_lag_12_differences():
    months = pd.date_range("2020-01-01", periods=24, freq="MS")
    df = pd.DataFrame({"series_id": "a", "month_start": months, "y": list(range(12)) + [x + 5 for x in range(12)]})
    assert seasonal_scale(df, 12)["a"] == 5
