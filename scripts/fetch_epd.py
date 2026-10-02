"""Pull monthly English Prescribing Dataset (EPD) aggregates from the NHSBSA Open Data Portal.

Each raw EPD month has ~17M rows, so we aggregate server-side with the CKAN
`datastore_search_sql` endpoint down to region x BNF chapter (~165 rows/month).
One CSV per month is written to data/raw/epd/. Existing months are skipped,
so re-running only fetches missing or new months (incremental load).

Usage:
    python scripts/fetch_epd.py --start 202101
    python scripts/fetch_epd.py --start 202503 --end 202503 --force
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

BASE = "https://opendata.nhsbsa.net/api/3/action/"
DATASET_ID = "english-prescribing-dataset-epd-with-snomed-code"  # Nov 2020 onwards
RESOURCE_PATTERN = re.compile(r"^EPD_SNOMED_(\d{6})$")
OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "epd"

NUMERIC_COLS = ["ITEMS", "TOTAL_QUANTITY", "NIC", "ACTUAL_COST"]

# Some months store numeric columns as STRING (e.g. TOTAL_QUANTITY in 202503).
# Cast via STRING so the query works whatever the source type, and count failed casts.
AGG_SQL = """
SELECT
    YEAR_MONTH,
    REGIONAL_OFFICE_CODE,
    REGIONAL_OFFICE_NAME,
    BNF_CHAPTER_PLUS_CODE,
    {sums},
    COUNT(*) AS SOURCE_ROWS,
    {failures} AS CAST_FAILURES
FROM `{resource}`
GROUP BY YEAR_MONTH, REGIONAL_OFFICE_CODE, REGIONAL_OFFICE_NAME, BNF_CHAPTER_PLUS_CODE
"""


def build_sql(resource: str) -> str:
    num = lambda c: f"SAFE_CAST(CAST({c} AS STRING) AS FLOAT64)"
    sums = ",\n    ".join(f"SUM({num(c)}) AS {c}" for c in NUMERIC_COLS)
    failures = " + ".join(f"COUNTIF({c} IS NOT NULL AND {num(c)} IS NULL)" for c in NUMERIC_COLS)
    return AGG_SQL.format(resource=resource, sums=sums, failures=failures)


class ClientError(Exception):
    """4xx from the API: the request itself is wrong, retrying won't help."""


def get_json(session: requests.Session, url: str, params: dict, retries: int = 4) -> dict:
    for attempt in range(retries):
        try:
            r = session.get(url, params=params, timeout=300)
            if 400 <= r.status_code < 500 and r.status_code != 429:
                raise ClientError(f"HTTP {r.status_code}: {r.text[:1000]}")
            r.raise_for_status()
            payload = r.json()
            if not payload.get("success", False):
                raise RuntimeError(payload.get("error"))
            return payload["result"]
        except ClientError:
            raise
        except (requests.RequestException, RuntimeError, ValueError) as exc:
            wait = 2 ** attempt * 5
            print(f"  attempt {attempt + 1} failed ({exc}); retrying in {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"giving up after {retries} attempts")


def list_months(session: requests.Session) -> list[str]:
    result = get_json(session, BASE + "package_show", {"id": DATASET_ID})
    months = []
    for res in result["resources"]:
        m = RESOURCE_PATTERN.match(res.get("name", ""))
        if m:
            months.append(m.group(1))
    return sorted(months)


def fetch_month(session: requests.Session, yyyymm: str) -> pd.DataFrame:
    resource = f"EPD_SNOMED_{yyyymm}"
    result = get_json(
        session,
        BASE + "datastore_search_sql",
        {"resource_id": resource, "sql": build_sql(resource)},
    )
    df = pd.DataFrame.from_records(result["result"]["records"])
    df.columns = [c.upper() for c in df.columns]
    bad = int(pd.to_numeric(df.pop("CAST_FAILURES")).sum())
    if bad:
        raise RuntimeError(f"{bad} values in {resource} could not be converted to numbers")
    df["_SOURCE_RESOURCE"] = resource
    df["_LOADED_AT"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="202101", help="first month YYYYMM")
    ap.add_argument("--end", default=None, help="last month YYYYMM (default: latest)")
    ap.add_argument("--force", action="store_true", help="re-download existing months")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    months = [m for m in list_months(session) if m >= args.start and (args.end is None or m <= args.end)]
    print(f"{len(months)} months available in range {months[0]}..{months[-1]}")

    failed = {}
    for m in months:
        target = OUT_DIR / f"epd_{m}.csv"
        if target.exists() and not args.force:
            continue
        print(f"fetching {m}")
        try:
            df = fetch_month(session, m)
        except (ClientError, RuntimeError) as exc:
            print(f"  FAILED: {exc}", file=sys.stderr)
            failed[m] = str(exc)
            continue
        if df.empty:
            print(f"  WARNING: {m} returned no rows", file=sys.stderr)
            failed[m] = "empty result"
            continue
        df.to_csv(target, index=False)
        print(f"  {len(df)} rows, {int(df['ITEMS'].sum()):,} items")

    if failed:
        print(f"\n{len(failed)} month(s) failed: {', '.join(failed)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()