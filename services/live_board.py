from __future__ import annotations

from models import AvoidBet, BetGrade, HitPick, HitRunRbiPick, MoneylineLeg, Parlay, Pick, SettledPick, WorldCupMatchCard
from services.live_feed import (
    SPORT_NAMES,
    american_to_decimal,
    competition,
    decimal_to_american,
    event_time_et,
    fetch_all_scoreboards,
    implied_probability,
    matchup_name,
    odds_block,
    open_close_text,
    probability_to_american,
    team_moneylines,
    teams_for_event,
    today_key,
    total_market,
    venue_note,
    weather_note,
)
from utils import rank_picks


LEAGUE_LOGOS = {
    "MLB": "https://a.espncdn.com/i/teamlogos/leagues/500/mlb.png",
    "WNBA": "https://a.espncdn.com/i/teamlogos/leagues/500/wnba.png",
    "FIFA World Cup": "https://a.espncdn.com/i/leaguelogos/soccer/500/4.png",
}


def _grade(edge: float, confidence: float) -> BetGrade:
    if edge >= 7.5 and confidence >= 8.8:
        return BetGrade.A_PLUS
    if edge >= 5.0 and confidence >= 8.0:
        return BetGrade.A
    if edge >= 3.0 and confidence >= 7.2:
        return BetGrade.A_MINUS
    if edge >= 1.8 and confidence >= 6.6:
        return BetGrade.B_PLUS
    return BetGrade.NO_PLAY


def _stake(grade: BetGrade) -> str:
    return {
        BetGrade.A_PLUS: "1.25u",
        BetGrade.A: "1.0u",
        BetGrade.A_MINUS: "0.75u",
        BetGrade.B_PLUS: "0.4u",
        BetGrade.NO_PLAY: "0u",
    }[grade]


def _pick_from_moneyline(event: dict, league: str, side: str, odds: int, model_probability: float, rating_edge: float) -> Pick | None:
    implied = implied_probability(odds)
    edge = round((model_probability - implied) * 100, 1)
    confidence = round(min(9.4, max(5.5, 5.8 + edge * 0.42 + abs(rating_edge) * 0.02)), 1)
    grade = _grade(edge, confidence)
    if grade == BetGrade.NO_PLAY:
        return None

    teams = teams_for_event(event, league)
    if not teams:
        return None
    home, away = teams
    selected = home if side == "home" else away
    opponent = away if side == "home" else home
    return Pick(
        sport=SPORT_NAMES[league],
        league=league,
        market="Moneyline",
        selection=f"{selected.display_name} ML",
        matchup=matchup_name(event, league),
        start_time_et=event_time_et(event),
        image_url=selected.logo or LEAGUE_LOGOS[league],
        image_alt=selected.display_name,
        grade=grade,
        confidence=confidence,
        probability=round(model_probability * 100, 1),
        fair_odds=probability_to_american(model_probability),
        sportsbook_odds=odds,
        edge=edge,
        recommended_stake=_stake(grade),
        reasoning=(
            f"Live ESPN/DraftKings feed shows {selected.display_name} at {odds:+d}. "
            f"Record/stat model rates the matchup edge over {opponent.display_name}; "
            f"records: {selected.record} vs {opponent.record}. Venue: {venue_note(event)}."
        ),
        injury_notes="Team-level feed only. No player prop is approved without a verified player/lineup source.",
        weather_notes=weather_note(event),
        market_movement=open_close_text(event, side),
        simulation_support="Supports" if edge >= 4.5 else "Neutral",
    )


def _moneyline_candidates(event: dict, league: str) -> list[Pick]:
    teams = teams_for_event(event, league)
    if not teams:
        return []
    home, away = teams
    home_odds, away_odds = team_moneylines(event)
    candidates = []
    if home_odds is not None:
        rating_edge = home.rating - away.rating
        model_probability = min(0.86, max(0.12, implied_probability(home_odds) + rating_edge * 0.0035))
        pick = _pick_from_moneyline(event, league, "home", home_odds, model_probability, rating_edge)
        if pick:
            candidates.append(pick)
    if away_odds is not None:
        rating_edge = away.rating - home.rating
        model_probability = min(0.86, max(0.12, implied_probability(away_odds) + rating_edge * 0.0035))
        pick = _pick_from_moneyline(event, league, "away", away_odds, model_probability, rating_edge)
        if pick:
            candidates.append(pick)
    return candidates


def _total_candidate(event: dict, league: str) -> Pick | None:
    over_line, over_odds, under_line, under_odds = total_market(event)
    if not over_line or over_odds is None or under_odds is None:
        return None
    block = odds_block(event)
    over_open = (((block.get("total") or {}).get("over") or {}).get("open") or {}).get("line", "")
    under_open = (((block.get("total") or {}).get("under") or {}).get("open") or {}).get("line", "")
    if not over_open and not under_open:
        return None
    current_num = "".join(ch for ch in over_line if ch.isdigit() or ch == ".")
    open_num = "".join(ch for ch in str(over_open or under_open) if ch.isdigit() or ch == ".")
    try:
        current = float(current_num)
        opened = float(open_num)
    except ValueError:
        return None
    if abs(current - opened) < 0.5:
        return None

    if current < opened:
        selection = f"{matchup_name(event, league)} Under {current:g}"
        odds = under_odds
        movement = f"Total moved down from {opened:g} to {current:g}."
    else:
        selection = f"{matchup_name(event, league)} Over {current:g}"
        odds = over_odds
        movement = f"Total moved up from {opened:g} to {current:g}."
    model_probability = min(0.64, implied_probability(odds) + 0.035)
    edge = round((model_probability - implied_probability(odds)) * 100, 1)
    confidence = round(6.9 + edge * 0.25, 1)
    grade = _grade(edge, confidence)
    if grade == BetGrade.NO_PLAY:
        return None
    return Pick(
        sport=SPORT_NAMES[league],
        league=league,
        market="Total",
        selection=selection,
        matchup=matchup_name(event, league),
        start_time_et=event_time_et(event),
        image_url=LEAGUE_LOGOS[league],
        image_alt=league,
        grade=grade,
        confidence=confidence,
        probability=round(model_probability * 100, 1),
        fair_odds=probability_to_american(model_probability),
        sportsbook_odds=odds,
        edge=edge,
        recommended_stake=_stake(grade),
        reasoning="Live total movement is the only approved angle; no stale matchup is being injected.",
        injury_notes="No player-specific bet approved.",
        weather_notes=weather_note(event),
        market_movement=movement,
        simulation_support="Neutral",
    )


def _all_live_events() -> list[tuple[str, dict]]:
    boards = fetch_all_scoreboards(today_key())
    events: list[tuple[str, dict]] = []
    for league, board in boards.items():
        for event in board.get("events", []):
            state = ((competition(event).get("status") or event.get("status") or {}).get("type") or {}).get("state")
            if state in {"pre", "in"}:
                events.append((league, event))
    return events


def load_top_picks() -> list[Pick]:
    picks: list[Pick] = []
    for league, event in _all_live_events():
        picks.extend(_moneyline_candidates(event, league))
        total = _total_candidate(event, league)
        if total:
            picks.append(total)
    ranked = [pick for pick in rank_picks(picks) if pick.grade != BetGrade.NO_PLAY]
    if ranked:
        return ranked[:10]
    return [
        Pick(
            sport="All Sports",
            league="Live Feed",
            market="No Play",
            selection="No Play",
            matchup="No verified edge found",
            start_time_et="Refresh pending",
            image_url="https://a.espncdn.com/i/teamlogos/leagues/500/default.png",
            image_alt="No Play",
            grade=BetGrade.NO_PLAY,
            confidence=1.0,
            probability=0.0,
            fair_odds=0,
            sportsbook_odds=0,
            edge=0.0,
            recommended_stake="0u",
            reasoning="Live schedule/odds loaded, but no play cleared the edge and confidence thresholds.",
            injury_notes="No forced picks.",
            weather_notes="No forced picks.",
            market_movement="No forced picks.",
            simulation_support="Rejects",
        )
    ]


def load_hit_picks() -> list[HitPick]:
    return []


def load_hrr_picks() -> list[HitRunRbiPick]:
    return []


def load_moneyline_parlay() -> Parlay:
    legs = []
    for pick in load_top_picks():
        if pick.market == "Moneyline" and pick.grade in {BetGrade.A_PLUS, BetGrade.A, BetGrade.A_MINUS} and pick.confidence >= 7.2:
            legs.append(
                MoneylineLeg(
                    leg=pick.selection,
                    sport=pick.sport,
                    league=pick.league,
                    matchup=pick.matchup,
                    start_time_et=pick.start_time_et,
                    image_url=pick.image_url,
                    probability=pick.probability,
                    estimated_odds=pick.sportsbook_odds,
                    reason=pick.reasoning,
                    removable_for_safer_card=pick.grade == BetGrade.A_MINUS,
                )
            )
    legs = legs[:5]
    if len(legs) < 2:
        return Parlay(legs=[], combined_probability=0.0, estimated_odds=0, risk_rating="No Play", safer_removes=[])
    combined_probability = 1.0
    combined_decimal = 1.0
    for leg in legs:
        combined_probability *= leg.probability / 100
        combined_decimal *= american_to_decimal(leg.estimated_odds)
    safer_removes = [leg.leg for leg in legs if leg.removable_for_safer_card]
    return Parlay(
        legs=legs,
        combined_probability=round(combined_probability * 100, 1),
        estimated_odds=decimal_to_american(combined_decimal),
        risk_rating="Moderate" if len(legs) <= 3 else "High",
        safer_removes=safer_removes,
    )


def load_world_cup_cards() -> list[WorldCupMatchCard]:
    cards: list[WorldCupMatchCard] = []
    for league, event in _all_live_events():
        if league != "FIFA World Cup":
            continue
        over_line, over_odds, under_line, under_odds = total_market(event)
        block = odds_block(event)
        details = block.get("details", "No moneyline listed")
        cards.append(
            WorldCupMatchCard(
                match=matchup_name(event, league),
                start_time_et=event_time_et(event),
                image_url=LEAGUE_LOGOS["FIFA World Cup"],
                legs=[
                    "No Play - verified 3+ leg SGP price unavailable in public feed",
                    f"Listed market: {details}",
                    f"Listed total: {over_line or under_line or 'not listed'}",
                ],
                estimated_odds=0,
                estimated_probability=0.0,
                confidence=1.0,
                reasoning=(
                    "The public feed confirms the match and straight-market odds, but does not provide a verified "
                    "+100 same-game parlay price. The dashboard will not invent one."
                ),
                most_likely_score="No projection without xG/lineup feed",
                avoid_list=[
                    "Unverified same-game parlays",
                    "Anytime scorer props without confirmed lineups",
                    f"Blind chase on {details}",
                ],
            )
        )
    return cards


def load_pick_history() -> list[SettledPick]:
    return []


def load_avoid_bets() -> list[AvoidBet]:
    avoids: list[AvoidBet] = []
    for league, event in _all_live_events():
        teams = teams_for_event(event, league)
        if not teams:
            continue
        home, away = teams
        home_odds, away_odds = team_moneylines(event)
        for side, team, opponent, odds in (("home", home, away, home_odds), ("away", away, home, away_odds)):
            if odds is None:
                continue
            rating_edge = team.rating - opponent.rating
            model_probability = min(0.86, max(0.12, implied_probability(odds) + rating_edge * 0.0035))
            edge = (model_probability - implied_probability(odds)) * 100
            if odds <= -220 and edge < 2.0:
                avoids.append(
                    AvoidBet(
                        bet=f"{team.display_name} ML",
                        sport=SPORT_NAMES[league],
                        league=league,
                        matchup=matchup_name(event, league),
                        market="Moneyline",
                        sportsbook_odds=odds,
                        start_time_et=event_time_et(event),
                        image_url=team.logo or LEAGUE_LOGOS[league],
                        category="Overpriced favorite",
                        risk="High",
                        reason=(
                            f"Live market asks {odds:+d}, but the record/stat model shows only {edge:.1f}% edge. "
                            f"Do not pay premium juice without a cleaner projection gap."
                        ),
                    )
                )
        if league == "FIFA World Cup":
            avoids.append(
                AvoidBet(
                    bet=f"{matchup_name(event, league)} unverified 3+ leg SGP",
                    sport="Soccer",
                    league=league,
                    matchup=matchup_name(event, league),
                    market="Same-game parlay",
                    sportsbook_odds=0,
                    start_time_et=event_time_et(event),
                    image_url=LEAGUE_LOGOS[league],
                    category="Unverified market",
                    risk="Extreme",
                    reason="Public feed lists straight markets, not a verified combinable 3+ leg SGP price. No invented parlay.",
                )
            )
    return avoids[:10]
