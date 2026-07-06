from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

import requests


ET = ZoneInfo("America/New_York")

ESPN_ENDPOINTS = {
    "MLB": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard",
    "WNBA": "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard",
    "FIFA World Cup": "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard",
}

SPORT_NAMES = {
    "MLB": "MLB",
    "WNBA": "Basketball",
    "FIFA World Cup": "Soccer",
}


@dataclass(frozen=True)
class TeamSide:
    display_name: str
    abbreviation: str
    logo: str
    record: str
    win_pct: float
    rating: float
    home_away: str


def today_key(now: datetime | None = None) -> str:
    now = now or datetime.now(ET)
    return now.astimezone(ET).strftime("%Y%m%d")


def fetch_scoreboard(league: str, date_key: str | None = None) -> dict:
    url = ESPN_ENDPOINTS[league]
    params = {"dates": date_key or today_key()}
    response = requests.get(
        url,
        params=params,
        timeout=12,
        headers={"User-Agent": "PropPlugPat/1.0 (+streamlit dashboard)"},
    )
    response.raise_for_status()
    return response.json()


def fetch_all_scoreboards(date_key: str | None = None) -> dict[str, dict]:
    boards = {}
    for league in ESPN_ENDPOINTS:
        try:
            boards[league] = fetch_scoreboard(league, date_key)
        except requests.RequestException:
            boards[league] = {"events": []}
    return boards


def parse_american(value) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip().replace("+", "")
    try:
        return int(float(text))
    except ValueError:
        return None


def implied_probability(odds: int) -> float:
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    return 100 / (odds + 100)


def probability_to_american(probability: float) -> int:
    probability = min(max(probability, 0.01), 0.99)
    if probability >= 0.5:
        return round(-100 * probability / (1 - probability))
    return round(100 * (1 - probability) / probability)


def american_to_decimal(odds: int) -> float:
    if odds > 0:
        return 1 + odds / 100
    return 1 + 100 / abs(odds)


def decimal_to_american(decimal_odds: float) -> int:
    if decimal_odds >= 2:
        return round((decimal_odds - 1) * 100)
    return round(-100 / (decimal_odds - 1))


def event_time_et(event: dict) -> str:
    raw = event.get("date") or event.get("competitions", [{}])[0].get("date")
    if not raw:
        return "TBD"
    dt = datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(ET)
    return dt.strftime("%I:%M %p ET").lstrip("0")


def competition(event: dict) -> dict:
    return (event.get("competitions") or [{}])[0]


def odds_block(event: dict) -> dict:
    comp = competition(event)
    odds = comp.get("odds") or event.get("odds") or []
    return odds[0] if odds else {}


def _record_pct(summary: str) -> float:
    try:
        wins, losses = [int(part) for part in summary.split("-")[:2]]
    except (AttributeError, ValueError):
        return 0.5
    total = wins + losses
    return wins / total if total else 0.5


def _stat_value(team: dict, name: str, default: float = 0.0) -> float:
    for stat in team.get("statistics", []):
        if stat.get("name") == name:
            try:
                return float(str(stat.get("displayValue", "")).replace("%", ""))
            except ValueError:
                return default
    return default


def _pitcher_era(team: dict) -> float | None:
    for probable in team.get("probables", []):
        for stat in probable.get("statistics", []):
            if stat.get("name") == "ERA":
                try:
                    return float(stat.get("displayValue"))
                except (TypeError, ValueError):
                    return None
    return None


def _team_side(raw: dict, league: str) -> TeamSide:
    team = raw.get("team", {})
    record = "0-0"
    records = raw.get("records") or []
    if records:
        record = records[0].get("summary", "0-0")
    win_pct = _record_pct(record)
    rating = win_pct * 100
    if league == "MLB":
        runs = _stat_value(raw, "runs")
        era = _stat_value(raw, "ERA", 4.5)
        pitcher_era = _pitcher_era(raw)
        rating += runs / 25
        rating -= era * 2.0
        if pitcher_era is not None:
            rating -= pitcher_era * 1.2
    elif league == "WNBA":
        rating += _stat_value(raw, "avgPoints") / 3
        rating += _stat_value(raw, "fieldGoalPct") / 5
        rating += _stat_value(raw, "threePointPct") / 8
    elif league == "FIFA World Cup":
        form = raw.get("form", "")
        rating += form.count("W") * 7 + form.count("D") * 3 - form.count("L") * 4
    return TeamSide(
        display_name=team.get("displayName", "Unknown Team"),
        abbreviation=team.get("abbreviation", ""),
        logo=team.get("logo", ""),
        record=record,
        win_pct=win_pct,
        rating=rating,
        home_away=raw.get("homeAway", ""),
    )


def teams_for_event(event: dict, league: str) -> tuple[TeamSide, TeamSide] | None:
    competitors = competition(event).get("competitors") or []
    if len(competitors) < 2:
        return None
    home_raw = next((item for item in competitors if item.get("homeAway") == "home"), competitors[0])
    away_raw = next((item for item in competitors if item.get("homeAway") == "away"), competitors[1])
    return _team_side(home_raw, league), _team_side(away_raw, league)


def matchup_name(event: dict, league: str) -> str:
    teams = teams_for_event(event, league)
    if not teams:
        return event.get("name", "Unknown matchup")
    home, away = teams
    return f"{away.display_name} at {home.display_name}" if league != "FIFA World Cup" else f"{away.display_name} vs {home.display_name}"


def venue_note(event: dict) -> str:
    comp = competition(event)
    venue = comp.get("venue", {})
    name = venue.get("fullName") or venue.get("displayName")
    city = (venue.get("address") or {}).get("city")
    if name and city:
        return f"{name}, {city}"
    return name or "Venue not listed"


def weather_note(event: dict) -> str:
    weather = competition(event).get("weather") or {}
    if weather:
        temp = weather.get("temperature")
        display = weather.get("displayValue", "Weather listed")
        return f"{display}, {temp}F" if temp else display
    venue = competition(event).get("venue", {})
    if venue.get("indoor"):
        return "Indoor venue."
    return "No weather note listed in live feed."


def team_moneylines(event: dict) -> tuple[int | None, int | None]:
    block = odds_block(event)
    moneyline = block.get("moneyline") or {}
    home = parse_american(((moneyline.get("home") or {}).get("close") or {}).get("odds"))
    away = parse_american(((moneyline.get("away") or {}).get("close") or {}).get("odds"))
    return home, away


def open_close_text(event: dict, side: str) -> str:
    moneyline = (odds_block(event).get("moneyline") or {}).get(side) or {}
    close = parse_american((moneyline.get("close") or {}).get("odds"))
    open_odds = parse_american((moneyline.get("open") or {}).get("odds"))
    if close is None:
        return "No live moneyline listed."
    if open_odds is None:
        return f"Live moneyline {close:+d}; no open listed."
    return f"Moved from {open_odds:+d} to {close:+d}."


def total_market(event: dict) -> tuple[str, int | None, str, int | None]:
    total = odds_block(event).get("total") or {}
    over = total.get("over") or {}
    under = total.get("under") or {}
    over_close = over.get("close") or {}
    under_close = under.get("close") or {}
    return (
        str(over_close.get("line", "")),
        parse_american(over_close.get("odds")),
        str(under_close.get("line", "")),
        parse_american(under_close.get("odds")),
    )
