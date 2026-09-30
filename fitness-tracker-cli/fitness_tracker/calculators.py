"""Module 1 - Health metrics: BMI, BMR, TDEE, water intake (pure functions)."""
from fitness_tracker import config


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """BMI = weight (kg) / height (m)^2, rounded to 1 decimal."""
    if weight_kg <= 0 or height_cm <= 0:
        raise ValueError("Weight and height must be positive.")
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def calculate_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    """Basal Metabolic Rate using the Mifflin-St Jeor equation (kcal/day)."""
    if sex not in ("male", "female"):
        raise ValueError("sex must be 'male' or 'female'.")
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return round(base + (5 if sex == "male" else -161), 1)


def calculate_tdee(bmr: float, activity: str) -> float:
    """Total Daily Energy Expenditure = BMR x activity multiplier."""
    if activity not in config.ACTIVITY_LEVELS:
        raise ValueError(f"Unknown activity level: {activity}")
    return round(bmr * config.ACTIVITY_LEVELS[activity][1], 1)


def calculate_water_intake(weight_kg: float, activity: str) -> float:
    """Recommended water in litres: 35 ml/kg plus an activity bonus."""
    if activity not in config.ACTIVITY_LEVELS:
        raise ValueError(f"Unknown activity level: {activity}")
    base = weight_kg * config.WATER_ML_PER_KG / 1000
    return round(base + config.ACTIVITY_LEVELS[activity][2], 2)


def healthy_weight_range(height_cm: float) -> tuple:
    """Weight range (kg) that yields a 'normal' BMI for the given height."""
    height_m = height_cm / 100
    low = config.BMI_UNDERWEIGHT_MAX * height_m ** 2
    high = (config.BMI_NORMAL_MAX - 0.1) * height_m ** 2
    return round(low, 1), round(high, 1)
