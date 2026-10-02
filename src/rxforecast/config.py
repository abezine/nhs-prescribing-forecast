from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[2]
DUCKDB_PATH = Path(os.environ.get("DUCKDB_PATH", ROOT / "data" / "warehouse.duckdb"))
REPORTS_DIR = ROOT / "reports"

TARGET = "items"          # prescription items per region x BNF chapter x month
HORIZON = 3               # forecast 1..3 months ahead
SEASON = 12               # monthly data, yearly seasonality
N_FOLDS = 12              # rolling origins in the backtest (one year of origins)
LAGS = list(range(1, 13)) + [24]
RANDOM_STATE = 42
