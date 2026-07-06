from __future__ import annotations

import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

from services.live_board import (
    load_avoid_bets,
    load_hit_picks,
    load_hrr_picks,
    load_moneyline_parlay,
    load_pick_history,
    load_top_picks,
)
from utils import rank_picks


STOP_WORDS = {
    "about",
    "against",
    "any",
    "are",
    "bet",
    "can",
    "card",
    "for",
    "game",
    "good",
    "have",
    "like",
    "line",
    "match",
    "odds",
    "play",
    "should",
    "take",
    "tell",
    "the",
    "this",
    "today",
    "want",
    "what",
    "with",
    "would",
}


def fmt_odds(odds: int) -> str:
    return f"+{odds}" if odds > 0 else str(odds)


def fmt_units(value: float) -> str:
    prefix = "+" if value > 0 else ""
    return f"{prefix}{value:.2f}u"


def _tokens(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9.]+", text.lower())
        if len(token) > 2 and token not in STOP_WORDS
    ]


def _score(text: str, haystack: str) -> int:
    words = _tokens(text)
    lower_haystack = haystack.lower()
    score = sum(1 for word in words if word in lower_haystack)
    for phrase in ("full game ml", "draw no bet", "double chance", "over 2.5", "over 4.5", "under 3.5", "1+ hit"):
        if phrase in text.lower() and phrase in lower_haystack:
            score += 4
    return score


def _best_match(text: str, items: list[tuple[object, str]], minimum: int = 2) -> object | None:
    scored = [(item, _score(text, haystack)) for item, haystack in items]
    scored = [entry for entry in scored if entry[1] >= minimum]
    if not scored:
        return None
    return max(scored, key=lambda entry: entry[1])[0]


def pick_lines(picks, limit: int = 5) -> str:
    lines = []
    for index, pick in enumerate(picks[:limit], start=1):
        lines.append(
            f"{index}. {pick.selection} ({pick.league}, {pick.matchup}, {pick.start_time_et}) - "
            f"{pick.grade.value}, {pick.confidence:.1f}/10 confidence, {pick.probability:.1f}% probability, "
            f"{pick.edge:.1f}% edge, stake {pick.recommended_stake}. {pick.reasoning}"
        )
    return "\n".join(lines)


def avoid_lines(avoid, limit: int = 6) -> str:
    return "\n".join(
        f"{index}. Avoid {item.bet} ({item.matchup}, {item.start_time_et}, {fmt_odds(item.sportsbook_odds)}): "
        f"{item.category}, {item.risk} risk. {item.reason}"
        for index, item in enumerate(avoid[:limit], start=1)
    )


def tracker_summary(history: pd.DataFrame | None = None) -> str:
    if history is None:
        history = pd.DataFrame([pick.model_dump() for pick in load_pick_history()])
    if history.empty:
        return "No settled pick history is loaded yet."
    if "date" in history:
        history = history.copy()
        history["date"] = pd.to_datetime(history["date"]).dt.date
    today = datetime.now(ZoneInfo("America/New_York")).date()
    yesterday = today - timedelta(days=1)
    windows = {
        "All time": history,
        "This year": history[history["date"] >= today.replace(month=1, day=1)],
        "This month": history[history["date"] >= today.replace(day=1)],
        "This week": history[history["date"] >= today - timedelta(days=today.weekday())],
        "Yesterday": history[history["date"] == yesterday],
    }
    lines = []
    for label, frame in windows.items():
        units = float(frame["profit_units"].sum()) if not frame.empty else 0.0
        wins = int((frame["result"] == "Win").sum()) if not frame.empty else 0
        losses = int((frame["result"] == "Loss").sum()) if not frame.empty else 0
        pushes = int((frame["result"] == "Push").sum()) if not frame.empty else 0
        lines.append(f"{label}: {fmt_units(units)} ({wins}W-{losses}L-{pushes}P)")
    return "\n".join(lines)


def bankroll_answer(message: str) -> str:
    amounts = [float(match) for match in re.findall(r"\$?(\d+(?:\.\d+)?)", message)]
    bankroll = max(amounts) if amounts else None
    if bankroll is None:
        return (
            "Bankroll answer: use 1 unit as roughly 1% of bankroll, 0.25u-0.5u for leans, "
            "1u for strong A plays, and 1.25u only for the strongest A+ edges. Tell me your bankroll "
            "amount and I can convert the unit sizing to dollars."
        )
    unit = bankroll * 0.01
    return (
        f"With a ${bankroll:,.0f} bankroll, 1u = ${unit:,.2f}.\n"
        f"A+ max stake: 1.25u = ${unit * 1.25:,.2f}. A play: 1u = ${unit:,.2f}. "
        f"B+ lean: 0.5u = ${unit * 0.5:,.2f}. Keep parlays small and cap total daily exposure."
    )


def _approved_play_answer(pick) -> str:
    return (
        f"Yes, this is on the approved board: {pick.selection}.\n\n"
        f"Game time: {pick.start_time_et}. Matchup: {pick.matchup}. Grade {pick.grade.value}, "
        f"{pick.confidence:.1f}/10 confidence, {pick.probability:.1f}% projected probability, "
        f"{pick.edge:.1f}% edge. Recommended stake: {pick.recommended_stake}.\n\n"
        f"Why: {pick.reasoning} Injury/lineup note: {pick.injury_notes} Market note: {pick.market_movement} "
        f"Simulation: {pick.simulation_support}."
    )


def _avoid_answer(item) -> str:
    return (
        f"Pass. I would not bet {item.bet} at {fmt_odds(item.sportsbook_odds)} right now.\n\n"
        f"Game time: {item.start_time_et}. Matchup: {item.matchup}. Flag: {item.category}, {item.risk} risk. "
        f"{item.reason}"
    )


def _hit_pick_answer(pick) -> str:
    return (
        f"Playable MLB hit prop: {pick.player} 1+ Hit.\n\n"
        f"Game time: {pick.start_time_et}. {pick.team} vs {pick.opponent}. Grade {pick.grade.value}, "
        f"{pick.confidence:.1f}/10 confidence, {pick.hit_probability:.1f}% hit probability. "
        f"Matchup: {pick.pitcher_matchup}; handedness: {pick.handedness_matchup}; batting order: {pick.batting_order_spot}. "
        f"{pick.reasoning}"
    )


def _hrr_pick_answer(pick) -> str:
    return (
        f"Playable MLB hit/run/RBI prop: {pick.player} 1+ Hit/Run/RBI.\n\n"
        f"Game time: {pick.start_time_et}. {pick.team} vs {pick.opponent}. Grade {pick.grade.value}, "
        f"{pick.confidence:.1f}/10 confidence, {pick.probability:.1f}% projected probability. "
        f"Implied team total: {pick.implied_team_total}; order spot: {pick.batting_order_spot}; run environment: {pick.run_environment}. "
        f"{pick.reasoning}"
    )


def _specific_play_answer(text: str) -> str | None:
    avoids = load_avoid_bets()
    avoid_match = _best_match(
        text,
        [
            (item, f"{item.bet} {item.matchup} {item.market} {item.sport} {item.league} {item.category}")
            for item in avoids
        ],
    )
    if avoid_match:
        return _avoid_answer(avoid_match)

    ranked = rank_picks(load_top_picks())
    pick_match = _best_match(
        text,
        [
            (pick, f"{pick.selection} {pick.matchup} {pick.market} {pick.sport} {pick.league}")
            for pick in ranked
        ],
    )
    if pick_match:
        return _approved_play_answer(pick_match)

    hit_match = _best_match(
        text,
        [
            (pick, f"{pick.player} {pick.team} {pick.opponent} 1+ hit {pick.pitcher_matchup}")
            for pick in load_hit_picks()
        ],
    )
    if hit_match:
        return _hit_pick_answer(hit_match)

    hrr_match = _best_match(
        text,
        [
            (pick, f"{pick.player} {pick.team} {pick.opponent} hit run rbi hrr {pick.run_environment}")
            for pick in load_hrr_picks()
        ],
    )
    if hrr_match:
        return _hrr_pick_answer(hrr_match)

    if any(term in text.lower() for term in ["should i", "what about", "worth", "take ", "bet "]):
        return (
            "No Play from the current board. I do not have enough edge in the live feed to approve that bet, "
            "and it is not one of the listed high-confidence plays. I would pass unless you can confirm a better "
            "price, clean lineup/injury news, and a projection edge."
        )
    return None


def chatbot_response(prompt: str) -> str:
    text = prompt.lower().strip()
    ranked = rank_picks(load_top_picks())

    if any(term in text for term in ["bankroll", "stake", "unit", "wager", "$"]):
        return bankroll_answer(prompt)

    specific_answer = _specific_play_answer(prompt)
    if specific_answer:
        return specific_answer

    if any(term in text for term in ["avoid", "trap", "do not", "don't bet", "dont bet"]):
        return "Specific plays to avoid right now:\n\n" + avoid_lines(load_avoid_bets())

    if any(term in text for term in ["tracker", "profit", "loss", "p/l", "record", "settled"]):
        return "Current tracked unit performance:\n\n" + tracker_summary()

    if "parlay" in text:
        parlay = load_moneyline_parlay()
        legs = "\n".join(
            f"- {leg.leg} ({leg.league}, {leg.matchup}, {leg.start_time_et}) at {fmt_odds(leg.estimated_odds)}: {leg.reason}"
            for leg in parlay.legs
        )
        removes = ", ".join(parlay.safer_removes) or "No removal suggested."
        return (
            f"Best strict moneyline parlay: {fmt_odds(parlay.estimated_odds)}, "
            f"{parlay.combined_probability:.1f}% combined probability, risk {parlay.risk_rating}.\n\n"
            f"{legs}\n\nSafer-card remove: {removes}"
        )

    if "mlb" in text and ("hit" in text or "hrr" in text or "rbi" in text or "run" in text):
        if not load_hit_picks() and not load_hrr_picks():
            return (
                "No Play on MLB player props right now. The live public feed does not expose verified hitter prop "
                "odds or confirmed batting orders, so I will not invent 1+ hit, run, or RBI picks."
            )
        hits = "\n".join(
            f"- {pick.player} 1+ hit ({pick.team} vs {pick.opponent}, {pick.start_time_et}): "
            f"{pick.hit_probability:.1f}%, {pick.grade.value}. {pick.reasoning}"
            for pick in load_hit_picks()
        )
        hrr = "\n".join(
            f"- {pick.player} hit/run/RBI ({pick.team} vs {pick.opponent}, {pick.start_time_et}): "
            f"{pick.probability:.1f}%, {pick.grade.value}. {pick.reasoning}"
            for pick in load_hrr_picks()
        )
        return f"Best MLB hit props:\n{hits}\n\nBest MLB hit/run/RBI props:\n{hrr}"

    if "wnba" in text:
        picks = [pick for pick in ranked if pick.league == "WNBA"]
        return "WNBA board:\n\n" + (pick_lines(picks) if picks else "No WNBA play meets the current threshold.")

    if "world cup" in text or "fifa" in text or "soccer" in text:
        picks = [pick for pick in ranked if pick.league == "FIFA World Cup"]
        return "FIFA World Cup board:\n\n" + (pick_lines(picks) if picks else "No World Cup play meets the current threshold.")

    if "tennis" in text or "wta" in text:
        picks = [pick for pick in ranked if pick.league == "WTA"]
        return "WTA/Tennis board:\n\n" + (pick_lines(picks) if picks else "No tennis play meets the current threshold.")

    if any(term in text for term in ["best", "top", "rank", "today", "board", "pick"]):
        return "Top ranked plays right now:\n\n" + pick_lines(ranked, limit=10)

    return (
        "Ask me a specific betting question and I will answer it directly. For example: "
        "'Should I bet the Dodgers ML?', 'What about USA vs Belgium over 2.5?', "
        "'Give me WNBA only', 'What should I avoid?', or 'My bankroll is $500, what should I stake?'"
    )
