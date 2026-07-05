from __future__ import annotations

import numpy as np

from models import SimulationResult


def _distribution(labels: list[str], weights: list[float]) -> dict[str, float]:
    total = float(sum(weights))
    return {label: round(weight / total * 100, 1) for label, weight in zip(labels, weights)}


def run_mlb_simulation(seed: int = 42) -> SimulationResult:
    rng = np.random.default_rng(seed)
    dodgers_runs = rng.poisson(lam=5.1, size=8000)
    dbacks_runs = rng.poisson(lam=3.9, size=8000)
    over_45 = float(np.mean(dodgers_runs >= 5) * 100)
    return SimulationResult(
        sport="MLB",
        matchup="Dodgers vs Diamondbacks",
        most_likely_outcomes=["Dodgers 5-4", "Dodgers 6-3", "Dodgers 4-3"],
        probability_distribution=_distribution(["Dodgers win", "Diamondbacks win", "One-run game"], [58, 42, 29]),
        projected_score="Dodgers 5.1, Diamondbacks 3.9",
        bet_probability=round(over_45, 1),
        confidence_rating=8.1,
        verdict="Supports",
    )


def run_soccer_simulation(seed: int = 7) -> SimulationResult:
    rng = np.random.default_rng(seed)
    brazil_goals = rng.poisson(lam=1.85, size=10000)
    norway_goals = rng.poisson(lam=0.98, size=10000)
    brazil_or_draw = float(np.mean(brazil_goals >= norway_goals) * 100)
    return SimulationResult(
        sport="Soccer",
        matchup="Brazil vs Norway",
        most_likely_outcomes=["Brazil 2-1", "Brazil 1-0", "Draw 1-1"],
        probability_distribution=_distribution(["Brazil win", "Draw", "Norway win"], [54, 24, 22]),
        projected_score="Brazil 1.85, Norway 0.98",
        bet_probability=round(brazil_or_draw, 1),
        confidence_rating=8.0,
        verdict="Supports",
    )


def run_wnba_simulation(seed: int = 18) -> SimulationResult:
    rng = np.random.default_rng(seed)
    aces = rng.normal(loc=87, scale=10, size=7000)
    opponent = rng.normal(loc=80, scale=11, size=7000)
    win_probability = float(np.mean(aces > opponent) * 100)
    return SimulationResult(
        sport="WNBA",
        matchup="Aces vs Sun",
        most_likely_outcomes=["Aces by 7", "Aces by 4", "Aces by 11"],
        probability_distribution=_distribution(["Aces win", "Sun win", "Overtime"], [70, 28, 2]),
        projected_score="Aces 87, Sun 80",
        bet_probability=round(win_probability, 1),
        confidence_rating=8.7,
        verdict="Supports",
    )


def run_all_simulations() -> list[SimulationResult]:
    return [run_mlb_simulation(), run_soccer_simulation(), run_wnba_simulation()]
