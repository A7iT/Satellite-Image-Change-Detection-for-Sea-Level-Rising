from pathlib import Path

# ==========================================================
# Project Root
# ==========================================================

ROOT = Path(__file__).resolve().parent.parent

# ==========================================================
# Configuration
# ==========================================================

CONFIG = ROOT / "config"

# ==========================================================
# Data Root
# ==========================================================

DATA = ROOT / "data"

# ==========================================================
# Processing Stages
# ==========================================================

RAW = DATA / "raw"
PROCESSED = DATA / "processed"
COMPOSITES = DATA / "composites"
INDICES = DATA / "indices"
WATER = DATA / "water"
ANALYSIS = DATA / "analysis"
STATISTICS = DATA / "statistics"
VISUALIZATION = DATA / "visualization"

# ==========================================================
# Project Resources
# ==========================================================

LOGS = ROOT / "logs"
NOTEBOOKS = ROOT / "notebooks"
RESULTS = ROOT / "results"
SHAPEFILES = ROOT / "shapefiles"