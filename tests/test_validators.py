import pytest
from fitness_tracker import validators as v


def test_valid_inputs():
    assert v.validate_name("  Ravi ") == "Ravi"
    assert v.validate_age("25") == 25
    assert v.validate_sex("M") == "male"
    assert v.validate_sex("female") == "female"
    assert v.validate_height_cm("172.5") == 172.5
    assert v.validate_weight_kg("68") == 68.0
    assert v.validate_activity("3") == "moderate"
    assert v.validate_activity("light") == "light"
    assert v.validate_record_id("4") == 4


@pytest.mark.parametrize("fn,bad", [
    (v.validate_name, "   "), (v.validate_name, "x" * 51),
    (v.validate_age, "abc"), (v.validate_age, "25.5"), (v.validate_age, "5"), (v.validate_age, "150"),
    (v.validate_sex, "x"),
    (v.validate_height_cm, "50"), (v.validate_height_cm, "nan"), (v.validate_height_cm, "inf"),
    (v.validate_weight_kg, "-3"), (v.validate_weight_kg, "1000"), (v.validate_weight_kg, ""),
    (v.validate_activity, "0"), (v.validate_activity, "6"), (v.validate_activity, "fly"),
    (v.validate_record_id, "0"), (v.validate_record_id, "-1"), (v.validate_record_id, "x"),
    (v.validate_note, "n" * 201),
])
def test_invalid_inputs(fn, bad):
    with pytest.raises(v.ValidationError):
        fn(bad)


def test_boundaries_accepted():
    assert v.validate_age("15") == 15 and v.validate_age("100") == 100
    assert v.validate_height_cm("100") == 100.0
    assert v.validate_weight_kg("300") == 300.0
