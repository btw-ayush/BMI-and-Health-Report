import dataclasses
import pytest
from fitness_tracker import advice, analytics
from fitness_tracker.services import build_assessment


def _entry(profile, weight, ts, rid):
    p = dataclasses.replace(profile, weight_kg=weight)
    a = build_assessment(p)
    a.timestamp, a.id = ts, rid
    return a


def test_empty_history_is_none():
    assert analytics.summarize_progress([]) is None


def test_losing_trend(profile):
    hist = [_entry(profile, 70, "2026-01-01T10:00:00", 1),
            _entry(profile, 66, "2026-02-01T10:00:00", 2)]
    s = analytics.summarize_progress(hist)
    assert s["trend"] == "losing" and s["weight_change"] == -4.0 and s["entries"] == 2


def test_gaining_and_stable(profile):
    up = [_entry(profile, 60, "2026-01-01T10:00:00", 1), _entry(profile, 63, "2026-02-01T10:00:00", 2)]
    assert analytics.summarize_progress(up)["trend"] == "gaining"
    flat = [_entry(profile, 60, "2026-01-01T10:00:00", 1), _entry(profile, 60.3, "2026-02-01T10:00:00", 2)]
    assert analytics.summarize_progress(flat)["trend"] == "stable"


def test_unsorted_input_handled(profile):
    hist = [_entry(profile, 66, "2026-02-01T10:00:00", 2), _entry(profile, 70, "2026-01-01T10:00:00", 1)]
    assert analytics.summarize_progress(hist)["first_weight"] == 70


def test_advice_by_category():
    for cat in ("underweight", "normal", "overweight", "obese"):
        assert len(advice.get_advice(cat, "moderate")) >= 3
    assert len(advice.get_advice("normal", "sedentary")) == 4
    with pytest.raises(ValueError):
        advice.get_advice("bad", "light")
