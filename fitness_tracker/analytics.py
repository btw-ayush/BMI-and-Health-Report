"""Module 3b - Progress analytics over saved history."""
from typing import List, Optional

from fitness_tracker import config
from fitness_tracker.models import Assessment


def summarize_progress(history: List[Assessment]) -> Optional[dict]:
    """Return a progress summary, or None when there is no history."""
    if not history:
        return None
    ordered = sorted(history, key=lambda a: (a.timestamp, a.id or 0))
    first, latest = ordered[0], ordered[-1]
    change = round(latest.profile.weight_kg - first.profile.weight_kg, 1)
    if change > config.STABLE_WEIGHT_TOLERANCE_KG:
        trend = "gaining"
    elif change < -config.STABLE_WEIGHT_TOLERANCE_KG:
        trend = "losing"
    else:
        trend = "stable"
    return {
        "entries": len(ordered),
        "first_date": first.timestamp,
        "latest_date": latest.timestamp,
        "first_weight": first.profile.weight_kg,
        "latest_weight": latest.profile.weight_kg,
        "weight_change": change,
        "trend": trend,
        "average_bmi": round(sum(a.bmi for a in ordered) / len(ordered), 1),
        "latest_category": latest.category,
    }
