import pytest
from fitness_tracker import calculators as c


def test_bmi_happy_path():
    assert c.calculate_bmi(70, 175) == 22.9


@pytest.mark.parametrize("w,h", [(0, 170), (70, 0), (-5, 170)])
def test_bmi_rejects_non_positive(w, h):
    with pytest.raises(ValueError):
        c.calculate_bmi(w, h)


def test_bmr_male_and_female():
    assert c.calculate_bmr(70, 175, 30, "male") == 1648.8
    assert c.calculate_bmr(60, 160, 25, "female") == 1314.0


def test_bmr_invalid_sex():
    with pytest.raises(ValueError):
        c.calculate_bmr(70, 175, 30, "other")


def test_tdee_multiplier():
    assert c.calculate_tdee(1600, "sedentary") == 1920.0
    assert c.calculate_tdee(1600, "very_active") == 3040.0


def test_tdee_unknown_activity():
    with pytest.raises(ValueError):
        c.calculate_tdee(1600, "couch")


def test_water_intake():
    assert c.calculate_water_intake(70, "sedentary") == 2.45
    assert c.calculate_water_intake(70, "very_active") == 3.45


def test_healthy_weight_range():
    low, high = c.healthy_weight_range(170)
    assert low == 53.5 and high == 72.0
