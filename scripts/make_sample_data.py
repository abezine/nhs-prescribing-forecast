"""Generate synthetic data with the exact schema fetch_epd.py produces.

Used by CI and for offline development, so the pipeline never depends on the
NHSBSA API being up. Numbers are synthetic; only the structure matches.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "epd"

REGIONS = {
    "Y56": ("LONDON", 1.00),
    "Y58": ("SOUTH WEST", 0.75),
    "Y59": ("SOUTH EAST", 1.15),
    "Y60": ("MIDLANDS", 1.35),
    "Y61": ("EAST OF ENGLAND", 0.85),
    "Y62": ("NORTH WEST", 1.05),
    "Y63": ("NORTH EAST AND YORKSHIRE", 1.10),
}
CHAPTERS = {
    "01": ("Gastro-Intestinal System", 5.0e5, 0.00),
    "02": ("Cardiovascular System", 1.6e6, 0.00),
    "03": ("Respiratory System", 4.5e5, 0.25),
    "04": ("Central Nervous System", 1.4e6, 0.02),
    "05": ("Infections", 2.0e5, 0.35),
    "06": ("Endocrine System", 7.0e5, 0.00),
    "07": ("Obstetrics, Gynaecology and Urinary-Tract Disorders", 2.0e5, 0.00),
    "08": ("Malignant Disease and Immunosuppression", 3.0e4, 0.00),
    "09": ("Nutrition and Blood", 3.0e5, 0.05),
    "10": ("Musculoskeletal and Joint Diseases", 1.5e5, 0.03),
    "11": ("Eye", 6.0e4, 0.08),
    "12": ("Ear, Nose and Oropharynx", 5.0e4, 0.20),
    "13": ("Skin", 1.5e5, 0.10),
    "14": ("Immunological Products and Vaccines", 1.0e4, 0.40),
    "15": ("Anaesthesia", 1.0e4, 0.00),
    "21": ("Appliances", 8.0e4, 0.00),
}


def main(start: str = "2021-01", end: str = "2026-07", seed: int = 42) -> None:
    rng = np.random.default_rng(seed)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    months = pd.period_range(start, end, freq="M")

    for i, p in enumerate(months):
        rows = []
        # winter peak (Dec/Jan) for seasonal chapters
        season = np.cos(2 * np.pi * (p.month - 1) / 12)
        working_days = 20 + (p.month not in (2, 12)) * 1.5
        for rcode, (rname, rscale) in REGIONS.items():
            for ccode, (cname, base, amp) in CHAPTERS.items():
                trend = 1 + 0.004 * i
                level = base * rscale * trend * (1 + amp * season) * working_days / 21
                items = max(0, rng.normal(level, 0.03 * level))
                cost_per_item = rng.uniform(6, 14) if ccode != "08" else rng.uniform(80, 120)
                rows.append(
                    {
                        "YEAR_MONTH": int(p.strftime("%Y%m")),
                        "REGIONAL_OFFICE_CODE": rcode,
                        "REGIONAL_OFFICE_NAME": rname,
                        "BNF_CHAPTER_PLUS_CODE": f"{ccode}: {cname}",
                        "ITEMS": round(items),
                        "TOTAL_QUANTITY": round(items * rng.uniform(25, 60)),
                        "NIC": round(items * cost_per_item, 2),
                        "ACTUAL_COST": round(items * cost_per_item * 0.93, 2),
                        "SOURCE_ROWS": int(rng.integers(8000, 20000)),
                    }
                )
        # the real data contains prescriptions not attributable to a region
        rows.append(
            {
                "YEAR_MONTH": int(p.strftime("%Y%m")),
                "REGIONAL_OFFICE_CODE": "-",
                "REGIONAL_OFFICE_NAME": "UNIDENTIFIED",
                "BNF_CHAPTER_PLUS_CODE": "04: Central Nervous System",
                "ITEMS": int(rng.integers(50, 500)),
                "TOTAL_QUANTITY": 1000,
                "NIC": 500.0,
                "ACTUAL_COST": 460.0,
                "SOURCE_ROWS": 12,
            }
        )
        df = pd.DataFrame(rows)
        df["_SOURCE_RESOURCE"] = f"EPD_SNOMED_{p.strftime('%Y%m')}"
        df["_LOADED_AT"] = pd.Timestamp.now(tz="UTC").isoformat(timespec="seconds")
        df.to_csv(OUT_DIR / f"epd_{p.strftime('%Y%m')}.csv", index=False)

    print(f"wrote {len(months)} synthetic months to {OUT_DIR}")


if __name__ == "__main__":
    main()
