"""The checks every Thalovant skill keeps: locales complete, packaging sound."""
from pathlib import Path

from thalovant_skillkit.checks import check_all


def test_the_skill_keeps_its_contracts():
    assert check_all(Path(__file__).parents[1]) == []
