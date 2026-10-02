"""Run the backtest, write evaluation artefacts, fit the final model and forecast.

python -m rxforecast.train
"""
from __future__ import annotations

import json

import pandas as pd

from . import backtest
from . import model as mdl
from .config import HORIZON, N_FOLDS, REPORTS_DIR
from .data import load_series
from .features import build_frame
from .metrics import summarise


def evaluate(preds: pd.DataFrame, df: pd.DataFrame) -> dict:
    labels = df.drop_duplicates("series_id").set_index("series_id")[["bnf_chapter_code", "bnf_chapter_name"]]
    p = preds.join(labels, on="series_id")
    out = {
        "overall": {m: summarise(g) for m, g in p.groupby("model")},
        "by_horizon": {
            f"h{h}": {m: summarise(g) for m, g in gh.groupby("model")} for h, gh in p.groupby("h")
        },
        "by_chapter_wape": {
            f"{c} {n}": {m: summarise(g)["WAPE"] for m, g in gc.groupby("model")}
            for (c, n), gc in p.groupby(["bnf_chapter_code", "bnf_chapter_name"])
        },
    }
    return out


def write_markdown(metrics: dict, n_series: int, first: str, last: str) -> str:
    models = ["hgb", "seasonal_naive", "naive_last"]
    lines = [
        "# Backtest results",
        "",
        f"Rolling-origin backtest, {N_FOLDS} origins, horizons 1-{HORIZON} months, "
        f"{n_series} series (NHS region x BNF chapter), data {first} to {last}.",
        "",
        "## Overall",
        "",
        "| model | MAE (items) | WAPE | MASE |",
        "|---|---:|---:|---:|",
    ]
    for m in models:
        s = metrics["overall"][m]
        lines.append(f"| {m} | {s['MAE']:,.0f} | {s['WAPE']:.2%} | {s['MASE']:.3f} |")
    lines += ["", "## WAPE by horizon", "", "| horizon | " + " | ".join(models) + " |", "|---|" + "---:|" * len(models)]
    for h, d in metrics["by_horizon"].items():
        lines.append(f"| {h} | " + " | ".join(f"{d[m]['WAPE']:.2%}" for m in models) + " |")
    lines += ["", "## WAPE by BNF chapter", "", "| chapter | " + " | ".join(models) + " | model wins |",
              "|---|" + "---:|" * len(models) + "---|"]
    for c, d in metrics["by_chapter_wape"].items():
        best_base = min(d["seasonal_naive"], d["naive_last"])
        win = "yes" if d["hgb"] < best_base else "**no**"
        lines.append(f"| {c} | " + " | ".join(f"{d[m]:.2%}" for m in models) + f" | {win} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    df = load_series()
    missing = int(df["is_missing"].sum())
    if missing:
        print(f"warning: {missing} missing series-months; affected lags are NaN (handled by the model)")

    frame = build_frame(df)
    print(f"{df['series_id'].nunique()} series, {frame['origin'].nunique()} usable origins")

    print("backtesting...")
    preds = backtest.run(df, frame)
    metrics = evaluate(preds, df)

    first, last = df["month_start"].min().strftime("%Y-%m"), df["month_start"].max().strftime("%Y-%m")
    (REPORTS_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (REPORTS_DIR / "evaluation.md").write_text(write_markdown(metrics, df["series_id"].nunique(), first, last))
    preds.to_parquet(REPORTS_DIR / "backtest_predictions.parquet", index=False)

    # final model on everything known, forecast from the last observed month
    final = mdl.fit(frame)
    full = build_frame(df, include_future=True)
    future = full[full["origin"] == full["origin"].max()].copy()
    future["yhat"] = mdl.predict(final, future)
    future[["series_id", "origin", "h", "target_month", "yhat"]].to_parquet(REPORTS_DIR / "forecast.parquet", index=False)

    df.to_parquet(REPORTS_DIR / "history.parquet", index=False)

    for m, s in metrics["overall"].items():
        print(f"{m:>15}: WAPE {s['WAPE']:.2%}  MASE {s['MASE']:.3f}")


if __name__ == "__main__":
    main()
