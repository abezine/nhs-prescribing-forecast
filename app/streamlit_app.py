"""Dashboard for the NHS prescribing forecast. Reads only files in reports/,
so it deploys to Streamlit Community Cloud without the warehouse."""
import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

REPORTS = Path(__file__).resolve().parents[1] / "reports"
MODEL_NAMES = {"hgb": "Gradient boosting", "seasonal_naive": "Seasonal naive", "naive_last": "Last value"}

st.set_page_config(page_title="NHS prescribing forecast", layout="wide")


@st.cache_data
def load():
    history = pd.read_parquet(REPORTS / "history.parquet")
    preds = pd.read_parquet(REPORTS / "backtest_predictions.parquet")
    forecast = pd.read_parquet(REPORTS / "forecast.parquet")
    metrics = json.loads((REPORTS / "metrics.json").read_text())
    return history, preds, forecast, metrics


if not (REPORTS / "metrics.json").exists():
    st.error("No results found in reports/. Run `make dbt train` first.")
    st.stop()

history, preds, forecast, metrics = load()

st.title("Forecasting NHS prescription items")
st.write(
    "Monthly prescription items in England by NHS region and BNF chapter, "
    "forecast 1 to 3 months ahead. Source: NHSBSA English Prescribing Dataset."
)

overall = metrics["overall"]
best_base = min(("seasonal_naive", "naive_last"), key=lambda m: overall[m]["WAPE"])
c1, c2, c3 = st.columns(3)
c1.metric("Model WAPE (backtest)", f"{overall['hgb']['WAPE']:.2%}")
c2.metric(f"Best baseline: {MODEL_NAMES[best_base]}", f"{overall[best_base]['WAPE']:.2%}")
gain = 1 - overall["hgb"]["WAPE"] / overall[best_base]["WAPE"]
c3.metric("Error reduction vs best baseline", f"{gain:.0%}")

# series selection
with st.sidebar:
    st.header("Series")
    regions = history.drop_duplicates("region_code").sort_values("region_name")
    region = st.selectbox("NHS region", regions["region_code"], format_func=dict(zip(regions.region_code, regions.region_name)).get)
    chapters = history.drop_duplicates("bnf_chapter_code").sort_values("bnf_chapter_code")
    chapter = st.selectbox(
        "BNF chapter", chapters["bnf_chapter_code"],
        format_func=lambda c: f"{c} {chapters.set_index('bnf_chapter_code').loc[c, 'bnf_chapter_name']}",
    )
    horizon = st.radio("Backtest horizon (months ahead)", [1, 2, 3], horizontal=True)

sid = f"{region}_{chapter}"
hist = history[history.series_id == sid][["month_start", "y"]].assign(series="Actual")
bt = preds[(preds.series_id == sid) & (preds.h == horizon) & (preds.model.isin(["hgb", "seasonal_naive"]))]
bt = bt.drop(columns="y").rename(columns={"target_month": "month_start", "yhat": "y"}).assign(series=lambda d: d.model.map(MODEL_NAMES) + " (backtest)")
fc = forecast[forecast.series_id == sid].rename(columns={"target_month": "month_start", "yhat": "y"}).assign(series="Forecast")

plot = pd.concat([hist, bt[["month_start", "y", "series"]], fc[["month_start", "y", "series"]]])
colors = alt.Scale(
    domain=["Actual", "Gradient boosting (backtest)", "Seasonal naive (backtest)", "Forecast"],
    range=["#1d2a3a", "#005eb8", "#a0a8b3", "#e07a1f"],
)
chart = (
    alt.Chart(plot)
    .mark_line(point=alt.OverlayMarkDef(size=25))
    .encode(
        x=alt.X("month_start:T", title=None),
        y=alt.Y("y:Q", title="Prescription items", scale=alt.Scale(zero=False)),
        color=alt.Color("series:N", scale=colors, legend=alt.Legend(orient="bottom", title=None)),
        tooltip=[alt.Tooltip("month_start:T", format="%b %Y"), "series", alt.Tooltip("y:Q", format=",.0f")],
    )
    .properties(height=380)
)
st.altair_chart(chart, use_container_width=True)

st.subheader("Where the model beats the baselines")
by_ch = pd.DataFrame(metrics["by_chapter_wape"]).T.reset_index(names="chapter")
long = by_ch.melt(id_vars="chapter", value_vars=["hgb", "seasonal_naive"], var_name="model", value_name="WAPE")
long["model"] = long["model"].map(MODEL_NAMES)
bars = (
    alt.Chart(long)
    .mark_bar()
    .encode(
        y=alt.Y("chapter:N", title=None, sort=None),
        x=alt.X("WAPE:Q", axis=alt.Axis(format="%")),
        color=alt.Color("model:N", scale=alt.Scale(range=["#005eb8", "#a0a8b3"]), legend=alt.Legend(orient="bottom", title=None)),
        yOffset="model:N",
        tooltip=["chapter", "model", alt.Tooltip("WAPE:Q", format=".2%")],
    )
    .properties(height=520)
)
st.altair_chart(bars, use_container_width=True)

with st.expander("Backtest method"):
    st.markdown(
        "Rolling-origin evaluation over the last 12 origins. At each origin the model is "
        "trained only on targets up to that month, then scored on the next 1 to 3 months. "
        "Baselines are scored on exactly the same rows. MASE is scaled by each series' "
        "in-sample seasonal-naive error, so values below 1 beat the seasonal naive forecast."
    )
    table = pd.DataFrame(overall).T.loc[["hgb", "seasonal_naive", "naive_last"]].rename(index=MODEL_NAMES)
    st.dataframe(table.style.format({"MAE": "{:,.0f}", "WAPE": "{:.2%}", "MASE": "{:.3f}", "n": "{:,}"}))
