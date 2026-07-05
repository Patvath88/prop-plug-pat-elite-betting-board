from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, computed_field, field_validator


class BetGrade(str, Enum):
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    B_PLUS = "B+"
    NO_PLAY = "No Play"


GRADE_SCORE = {
    BetGrade.A_PLUS: 4,
    BetGrade.A: 3,
    BetGrade.A_MINUS: 2,
    BetGrade.B_PLUS: 1,
    BetGrade.NO_PLAY: 0,
}


class Pick(BaseModel):
    sport: str
    market: str
    selection: str
    grade: BetGrade
    confidence: float = Field(ge=1, le=10)
    probability: float = Field(ge=0, le=100)
    fair_odds: int
    sportsbook_odds: int
    edge: float
    recommended_stake: str
    reasoning: str
    injury_notes: str
    weather_notes: str
    market_movement: str
    simulation_support: Literal["Supports", "Neutral", "Rejects", "No Data"]

    @computed_field
    @property
    def rank_score(self) -> float:
        return (
            GRADE_SCORE[self.grade] * 1000
            + self.confidence * 100
            + self.probability * 4
            + self.edge * 6
        )


class HitPick(BaseModel):
    player: str
    team: str
    opponent: str
    pitcher_matchup: str
    handedness_matchup: str
    batting_order_spot: int = Field(ge=1, le=9)
    recent_form: str
    hit_probability: float = Field(ge=0, le=100)
    confidence: float = Field(ge=1, le=10)
    grade: BetGrade
    reasoning: str


class HitRunRbiPick(BaseModel):
    player: str
    team: str
    opponent: str
    implied_team_total: float = Field(ge=0)
    batting_order_spot: int = Field(ge=1, le=9)
    recent_form: str
    run_environment: str
    probability: float = Field(ge=0, le=100)
    confidence: float = Field(ge=1, le=10)
    grade: BetGrade
    reasoning: str


class MoneylineLeg(BaseModel):
    leg: str
    sport: str
    probability: float = Field(ge=0, le=100)
    estimated_odds: int
    reason: str
    removable_for_safer_card: bool = False


class Parlay(BaseModel):
    legs: list[MoneylineLeg]
    combined_probability: float = Field(ge=0, le=100)
    estimated_odds: int
    risk_rating: Literal["Low", "Moderate", "High", "No Play"]
    safer_removes: list[str]

    @field_validator("legs")
    @classmethod
    def max_ten_legs(cls, value: list[MoneylineLeg]) -> list[MoneylineLeg]:
        if len(value) > 10:
            raise ValueError("Moneyline parlay cannot exceed 10 legs.")
        return value


class WorldCupMatchCard(BaseModel):
    match: str
    legs: list[str]
    estimated_odds: int
    estimated_probability: float = Field(ge=0, le=100)
    confidence: float = Field(ge=1, le=10)
    reasoning: str
    most_likely_score: str
    avoid_list: list[str]

    @field_validator("legs")
    @classmethod
    def at_least_three_legs(cls, value: list[str]) -> list[str]:
        if len(value) < 3:
            raise ValueError("World Cup card needs at least three legs.")
        return value


class AvoidBet(BaseModel):
    bet: str
    category: str
    risk: Literal["Medium", "High", "Extreme"]
    reason: str


class SimulationResult(BaseModel):
    sport: str
    matchup: str
    most_likely_outcomes: list[str]
    probability_distribution: dict[str, float]
    projected_score: str
    bet_probability: float = Field(ge=0, le=100)
    confidence_rating: float = Field(ge=1, le=10)
    verdict: Literal["Supports", "Neutral", "Rejects"]
