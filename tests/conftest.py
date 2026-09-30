import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fitness_tracker.models import UserProfile
from fitness_tracker.services import build_assessment


@pytest.fixture
def profile():
    return UserProfile("Asha", 25, "female", 165.0, 60.0, "moderate")


@pytest.fixture
def assessment(profile):
    return build_assessment(profile)
