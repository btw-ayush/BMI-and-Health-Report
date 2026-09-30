"""Service layer: turns a UserProfile into a complete Assessment."""
from fitness_tracker import calculators as calc
from fitness_tracker import classifier
from fitness_tracker.models import Assessment, UserProfile


def build_assessment(profile: UserProfile) -> Assessment:
    bmi = calc.calculate_bmi(profile.weight_kg, profile.height_cm)
    category = classifier.classify_bmi(bmi)
    bmr = calc.calculate_bmr(profile.weight_kg, profile.height_cm, profile.age, profile.sex)
    tdee = calc.calculate_tdee(bmr, profile.activity)
    low, high = calc.healthy_weight_range(profile.height_cm)
    return Assessment(
        profile=profile,
        bmi=bmi,
        category=category,
        bmr=bmr,
        tdee=tdee,
        target_calories=classifier.target_calories(tdee, category),
        water_liters=calc.calculate_water_intake(profile.weight_kg, profile.activity),
        healthy_min_kg=low,
        healthy_max_kg=high,
    )
