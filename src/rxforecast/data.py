import duckdb
import pandas as pd

from .config import DUCKDB_PATH, TARGET


def load_series(path=DUCKDB_PATH) -> pd.DataFrame:
    """Read the dbt mart. Returns long format: series_id, month_start, target + labels."""
    with duckdb.connect(str(path), read_only=True) as con:
        df = con.execute(
            f"""
            select series_id, month_start, region_code, region_name,
                   bnf_chapter_code, bnf_chapter_name, {TARGET} as y, is_missing
            from fct_prescribing_monthly
            order by series_id, month_start
            """
        ).df()
    df["month_start"] = pd.to_datetime(df["month_start"])
    return df
