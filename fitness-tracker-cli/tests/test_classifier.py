import pytest
from fitness_tracker import classifier as cl


@pytest.mark.parametrize("bmi,expected", [
    (10.0, "underweight"), (18.4, "underweight"),
    (18.5, "normal"), (24.9, "normal"),       # boundaries
    (25.0, "overweight"), (29.9, "overweight"),
    (30.0, "obese"), (45.0, "obese"),
])
def test_classify_bmi(bmi, expected):
    assert cl.classify_bmi(bmi) == expected


def test_classify_negative():
    with pytest.raises(ValueError):
        cl.classify_bmi(-1)


def test_target_calories():
    assert cl.target_calories(2000, "underweight") == 2300
    assert cl.target_calories(2000, "normal") == 2000
    assert cl.target_calories(2000, "obese") == 1500


def test_target_calories_unknown():
    with pytest.raises(ValueError):
        cl.target_calories(2000, "x")
