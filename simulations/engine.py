from __future__ import annotations

import numpy as np

from models import SimulationResult
from services.live_feed import fetch_all_scoreboards, matchup_name, teams_for_event, today_key


def _distribution(labels: list[str], weights: list[float]) -> dict[str, float]:
    total = float(sum(weights))
    return {label: round(weight / total * 100, 1) for label, weight in zip(labels, weights)}


def _simulation_for_event(league: str, event: dict, seed: int) -> SimulationResult | None:
    teams = teams_for_event(event, league)
    if not teams:
        return None
    home, away = teams
    rng = np.random.default_rng(seed)
    home_strength = max(0.2, home.rating / 100)
    away_strength = max(0.2, away.rating / 100)

    if league == "MLB":
        home_runs = rng.poisson(lam=3.2 + home_strength * 2.1, size=6000)
        away_runs = rng.poisson(lam=3.2 + away_strength * 2.1, size=6000)
        home_win = float(np.mean(home_runs > away_runs) * 100)
        return SimulationResult(
            sport="MLB",
            matchup=matchup_name(event, league),
            most_likely_outcomes=[
                f"{home.display_name} by 1",
                f"{away.display_name} by 1",
                "One-run game",
            ],
            probability_distribution=_distribution([f"{home.display_name} win", f"{away.display_name} win", "One-run game"], [home_win, 100 - home_win, 28]),
            projected_score=f"{home.display_name} {np.mean(home_runs):.1f}, {away.display_name} {np.mean(away_runs):.1f}",
            bet_probability=round(max(home_win, 100 - home_win), 1),
            confidence_rating=round(min(9.0, 5.5 + abs(home_win - 50) / 8), 1),
            verdict="Supports" if abs(home_win - 50) >= 8 else "Neutral",
        )

    if league == "WNBA":
        home_pts = rng.normal(loc=73 + home_strength * 18, scale=10, size=6000)
        away_pts = rng.normal(loc=73 + away_strength * 18, scale=10, size=6000)
        home_win = float(np.mean(home_pts > away_pts) * 100)
        return SimulationResult(
            sport="WNBA",
            matchup=matchup_name(event, league),
            most_likely_outcomes=[
                f"{home.display_name} by 4",
                f"{away.display_name} by 4",
                "Single-digit margin",
            ],
            probability_distribution=_distribution([f"{home.display_name} win", f"{away.display_name} win", "OT/coin-flip finish"], [home_win, 100 - home_win, 3]),
            projected_score=f"{home.display_name} {np.mean(home_pts):.1f}, {away.display_name} {np.mean(away_pts):.1f}",
            bet_probability=round(max(home_win, 100 - home_win), 1),
            confidence_rating=round(min(9.0, 5.5 + abs(home_win - 50) / 8), 1),
            verdict="Supports" if abs(home_win - 50) >= 8 else "Neutral",
        )

    if league == "FIFA World Cup":
        home_goals = rng.poisson(lam=0.8 + home_strength * 1.1, size=8000)
        away_goals = rng.poisson(lam=0.8 + away_strength * 1.1, size=8000)
        home_win = float(np.mean(home_goals > away_goals) * 100)
        draw = float(np.mean(home_goals == away_goals) * 100)
        away_win = 100 - home_win - draw
        return SimulationResult(
            sport="Soccer",
            matchup=matchup_name(event, league),
            most_likely_outcomes=[
                f"{home.display_name} 1-1 {away.display_name}",
                f"{home.display_name} 2-1 {away.display_name}",
                f"{away.display_name} 2-1 {home.display_name}",
            ],
            probability_distribution=_distribution([f"{home.display_name} win", "Draw", f"{away.display_name} win"], [home_win, draw, away_win]),
            projected_score=f"{home.display_name} {np.mean(home_goals):.2f}, {away.display_name} {np.mean(away_goals):.2f}",
            bet_probability=round(max(home_win, draw, away_win), 1),
            confidence_rating=round(min(8.5, 5.2 + max(home_win, draw, away_win) / 15), 1),
            verdict="Neutral",
        )
    return None


def run_all_simulations() -> list[SimulationResult]:
    boards = fetch_all_scoreboards(today_key())
    sims: list[SimulationResult] = []
    seed = 11
    for league in ("MLB", "WNBA", "FIFA World Cup"):
        for event in boards.get(league, {}).get("events", [])[:2]:
            sim = _simulation_for_event(league, event, seed)
            seed += 1
            if sim:
                sims.append(sim)
    return sims
