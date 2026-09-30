"""Central configuration and constants (single source of truth)."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_data_dir() -> Path:
    """Data directory; override with FITNESS_TRACKER_DATA env variable."""
    return Path(os.environ.get("FITNESS_TRACKER_DATA", PROJECT_ROOT / "data"))


def get_history_path() -> Path:
    return get_data_dir() / "history.json"


def get_log_path() -> Path:
    return Path(os.environ.get("FITNESS_TRACKER_LOGS", PROJECT_ROOT / "logs")) / "app.log"


# ---- Validation limits (Mifflin-St Jeor is intended for adults) ----
AGE_RANGE = (15, 100)
HEIGHT_CM_RANGE = (100.0, 250.0)
WEIGHT_KG_RANGE = (20.0, 300.0)
MAX_NAME_LENGTH = 50
MAX_NOTE_LENGTH = 200

# ---- WHO BMI thresholds ----
BMI_UNDERWEIGHT_MAX = 18.5
BMI_NORMAL_MAX = 25.0
BMI_OVERWEIGHT_MAX = 30.0

# ---- Activity levels: key -> (label, TDEE multiplier, extra water in litres) ----
ACTIVITY_LEVELS = {
    "sedentary": ("Sedentary (little/no exercise)", 1.2, 0.0),
    "light": ("Light (1-3 days/week)", 1.375, 0.3),
    "moderate": ("Moderate (3-5 days/week)", 1.55, 0.5),
    "active": ("Active (6-7 days/week)", 1.725, 0.7),
    "very_active": ("Very active (hard daily / physical job)", 1.9, 1.0),
}

WATER_ML_PER_KG = 35
CALORIE_ADJUSTMENT = {"underweight": 300, "normal": 0, "overweight": -500, "obese": -500}
STABLE_WEIGHT_TOLERANCE_KG = 0.5
