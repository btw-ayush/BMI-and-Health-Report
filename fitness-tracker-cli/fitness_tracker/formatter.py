"""Terminal output: ANSI colours (auto-disabled when unsupported) and layouts."""
import os
import sys
from typing import List

from fitness_tracker import config
from fitness_tracker.models import Assessment

_COLORS = {"red": "31", "green": "32", "yellow": "33", "blue": "34", "cyan": "36", "bold": "1"}
CATEGORY_COLOR = {"underweight": "yellow", "normal": "green", "overweight": "yellow", "obese": "red"}


def supports_color() -> bool:
    return sys.stdout.isatty() and "NO_COLOR" not in os.environ


def colorize(text: str, color: str, enabled: bool = True) -> str:
    if not enabled or color not in _COLORS:
        return text
    return f"\033[{_COLORS[color]}m{text}\033[0m"


def render_assessment(a: Assessment, color: bool = True) -> str:
    cat = colorize(a.category.upper(), CATEGORY_COLOR[a.category], color)
    p = a.profile
    lines = [
        colorize(f"--- Results for {p.name} ---", "cyan", color),
        f"BMI:                 {a.bmi}  ({cat})",
        f"Healthy weight:      {a.healthy_min_kg}-{a.healthy_max_kg} kg",
        f"BMR:                 {a.bmr:.0f} kcal/day",
        f"Maintenance (TDEE):  {a.tdee:.0f} kcal/day",
        f"Target calories:     {a.target_calories:.0f} kcal/day",
        f"Water intake:        {a.water_liters} L/day",
    ]
    return "\n".join(lines)


def render_advice(tips: List[str], color: bool = True) -> str:
    header = colorize("Suggestions:", "bold", color)
    return header + "\n" + "\n".join(f"  * {t}" for t in tips)


def render_history(history: List[Assessment], color: bool = True) -> str:
    if not history:
        return "No records yet."
    head = f"{'ID':<4}{'Date':<21}{'Name':<14}{'Weight':<9}{'BMI':<7}{'Category':<13}Note"
    rows = [colorize(head, "bold", color)]
    for a in history:
        cat = a.category.ljust(13)
        rows.append(
            f"{a.id:<4}{a.timestamp:<21}{a.profile.name[:12]:<14}"
            f"{a.profile.weight_kg:<9g}{a.bmi:<7}"
            f"{colorize(cat, CATEGORY_COLOR[a.category], color)}{a.note}"
        )
    return "\n".join(rows)


def render_progress(summary: dict, color: bool = True) -> str:
    if summary is None:
        return "No records yet - add an assessment first."
    trend_color = {"gaining": "yellow", "losing": "green", "stable": "cyan"}[summary["trend"]]
    sign = "+" if summary["weight_change"] > 0 else ""
    return "\n".join([
        colorize("--- Progress Report ---", "cyan", color),
        f"Entries:        {summary['entries']}",
        f"Period:         {summary['first_date']}  ->  {summary['latest_date']}",
        f"Weight:         {summary['first_weight']:g} kg -> {summary['latest_weight']:g} kg "
        f"({sign}{summary['weight_change']:g} kg)",
        f"Trend:          {colorize(summary['trend'], trend_color, color)}",
        f"Average BMI:    {summary['average_bmi']}",
        f"Latest status:  {colorize(summary['latest_category'], CATEGORY_COLOR[summary['latest_category']], color)}",
    ])


def activity_menu() -> str:
    return "\n".join(
        f"  {i}. {label}" for i, (label, _, _) in enumerate(config.ACTIVITY_LEVELS.values(), 1)
    )
