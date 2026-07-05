from __future__ import annotations

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

from models import Pick


REFRESH_TIMES_ET = [time(9, 0), time(12, 0), time(14, 0), time(18, 0), time(19, 0)]


def rank_picks(picks: list[Pick], limit: int = 10) -> list[Pick]:
    playable = [pick for pick in picks if pick.grade.value != "No Play" and pick.edge > 0]
    return sorted(playable, key=lambda pick: pick.rank_score, reverse=True)[:limit]


def get_next_refresh_time(now: datetime | None = None) -> datetime:
    eastern = ZoneInfo("America/New_York")
    current = now.astimezone(eastern) if now else datetime.now(eastern)
    for refresh_time in REFRESH_TIMES_ET:
        candidate = datetime.combine(current.date(), refresh_time, tzinfo=eastern)
        if candidate > current:
            return candidate
    return datetime.combine(current.date() + timedelta(days=1), REFRESH_TIMES_ET[0], tzinfo=eastern)


def american_to_decimal(odds: int) -> float:
    if odds > 0:
        return round(1 + odds / 100, 2)
    return round(1 + 100 / abs(odds), 2)


def grade_badge_class(grade: str) -> str:
    return {
        "A+": "grade-aplus",
        "A": "grade-a",
        "A-": "grade-aminus",
        "B+": "grade-bplus",
    }.get(grade, "grade-no-play")


def export_board_rows(picks: list[Pick]) -> pd.DataFrame:
    rows = [
        {
            "Sport": pick.sport,
            "Market": pick.market,
            "Selection": pick.selection,
            "Grade": pick.grade.value,
            "Confidence": pick.confidence,
            "Probability": pick.probability,
            "Fair Odds": pick.fair_odds,
            "Sportsbook Odds": pick.sportsbook_odds,
            "Edge": pick.edge,
            "Recommended Stake": pick.recommended_stake,
            "Reasoning": pick.reasoning,
            "Injury/Lineup Notes": pick.injury_notes,
            "Weather Notes": pick.weather_notes,
            "Market Movement": pick.market_movement,
            "Simulation Support": pick.simulation_support,
        }
        for pick in picks
    ]
    return pd.DataFrame(rows)
