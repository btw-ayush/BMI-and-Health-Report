"""Module 2 - BMI classification (WHO categories) and calorie targets."""
from fitness_tracker import config


def classify_bmi(bmi: float) -> str:
    """Return underweight | normal | overweight | obese."""
    if bmi < 0:
        raise ValueError("BMI cannot be negative.")
    if bmi < config.BMI_UNDERWEIGHT_MAX:
        return "underweight"
    if bmi < config.BMI_NORMAL_MAX:
        return "normal"
    if bmi < config.BMI_OVERWEIGHT_MAX:
        return "overweight"
    return "obese"


def target_calories(tdee: float, category: str) -> float:
    """Daily calorie target: TDEE adjusted for the BMI category."""
    if category not in config.CALORIE_ADJUSTMENT:
        raise ValueError(f"Unknown category: {category}")
    return round(tdee + config.CALORIE_ADJUSTMENT[category], 1)
