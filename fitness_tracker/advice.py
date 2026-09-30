"""Module 2 (cont.) - personalised wellness suggestions."""

_CATEGORY_ADVICE = {
    "underweight": [
        "Add calorie-dense, nutritious foods (nuts, dairy, whole grains).",
        "Prefer strength training to build muscle rather than only cardio.",
        "Eat 4-5 smaller meals through the day.",
    ],
    "normal": [
        "Great work! Maintain a balanced diet and regular routine.",
        "Mix cardio and strength training through the week.",
        "Keep sleep at 7-9 hours for recovery.",
    ],
    "overweight": [
        "Aim for a modest calorie deficit and gradual weight loss.",
        "Add 30 minutes of brisk walking or cycling most days.",
        "Cut back on sugary drinks and processed snacks.",
    ],
    "obese": [
        "Consider consulting a doctor or dietitian for a personalised plan.",
        "Start with low-impact activity (walking, swimming) and build up.",
        "Track meals and aim for slow, sustainable progress.",
    ],
}

_ACTIVITY_ADVICE = {
    "sedentary": "Try to stand or walk for a few minutes every hour.",
    "very_active": "Make sure you schedule rest days to avoid overtraining.",
}


def get_advice(category: str, activity: str) -> list:
    """Return a list of suggestion strings for the category and activity."""
    if category not in _CATEGORY_ADVICE:
        raise ValueError(f"Unknown category: {category}")
    tips = list(_CATEGORY_ADVICE[category])
    if activity in _ACTIVITY_ADVICE:
        tips.append(_ACTIVITY_ADVICE[activity])
    return tips
