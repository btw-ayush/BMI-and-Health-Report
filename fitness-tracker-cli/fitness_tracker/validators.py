"""Input validation. Every function takes raw text and returns a clean value
or raises ValidationError with a user-friendly message."""
import math

from fitness_tracker import config


class ValidationError(ValueError):
    """Raised when user input is invalid."""


def _to_float(raw: str, label: str) -> float:
    try:
        value = float(str(raw).strip())
    except ValueError:
        raise ValidationError(f"{label} must be a number.") from None
    if not math.isfinite(value):
        raise ValidationError(f"{label} must be a finite number.")
    return value


def _check_range(value: float, bounds: tuple, label: str, unit: str = "") -> None:
    low, high = bounds
    if not low <= value <= high:
        raise ValidationError(f"{label} must be between {low:g} and {high:g}{unit}.")


def validate_name(raw: str) -> str:
    name = str(raw).strip()
    if not name:
        raise ValidationError("Name cannot be empty.")
    if len(name) > config.MAX_NAME_LENGTH:
        raise ValidationError(f"Name must be at most {config.MAX_NAME_LENGTH} characters.")
    return name


def validate_age(raw: str) -> int:
    value = _to_float(raw, "Age")
    if value != int(value):
        raise ValidationError("Age must be a whole number.")
    _check_range(value, config.AGE_RANGE, "Age", " years")
    return int(value)


def validate_sex(raw: str) -> str:
    text = str(raw).strip().lower()
    if text in ("m", "male"):
        return "male"
    if text in ("f", "female"):
        return "female"
    raise ValidationError("Sex must be 'm' or 'f'.")


def validate_height_cm(raw: str) -> float:
    value = _to_float(raw, "Height")
    _check_range(value, config.HEIGHT_CM_RANGE, "Height", " cm")
    return value


def validate_weight_kg(raw: str) -> float:
    value = _to_float(raw, "Weight")
    _check_range(value, config.WEIGHT_KG_RANGE, "Weight", " kg")
    return value


def validate_activity(raw: str) -> str:
    """Accepts the menu number (1-5) or the level key (e.g. 'moderate')."""
    text = str(raw).strip().lower()
    keys = list(config.ACTIVITY_LEVELS)
    if text.isdigit() and 1 <= int(text) <= len(keys):
        return keys[int(text) - 1]
    if text in config.ACTIVITY_LEVELS:
        return text
    raise ValidationError(f"Choose an activity level from 1 to {len(keys)}.")


def validate_note(raw: str) -> str:
    note = str(raw).strip()
    if len(note) > config.MAX_NOTE_LENGTH:
        raise ValidationError(f"Note must be at most {config.MAX_NOTE_LENGTH} characters.")
    return note


def validate_record_id(raw: str) -> int:
    text = str(raw).strip()
    if not text.isdigit() or int(text) < 1:
        raise ValidationError("Record ID must be a positive whole number.")
    return int(text)
