"""Data models (dataclasses) shared by all modules."""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class UserProfile:
    name: str
    age: int
    sex: str  # "male" | "female"
    height_cm: float
    weight_kg: float
    activity: str  # key of config.ACTIVITY_LEVELS


@dataclass
class Assessment:
    profile: UserProfile
    bmi: float
    category: str  # underweight | normal | overweight | obese
    bmr: float
    tdee: float
    target_calories: float
    water_liters: float
    healthy_min_kg: float
    healthy_max_kg: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    id: Optional[int] = None
    note: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Assessment":
        data = dict(data)
        data["profile"] = UserProfile(**data["profile"])
        return cls(**data)
