from __future__ import annotations

from typing import Any

from .base import BaseAdapter


class OddsAPIAdapter(BaseAdapter):
    def fetch(self) -> dict[str, Any]:
        return {"status": "not_configured", "source": "odds_api", "markets": []}


class MLBStatsAdapter(BaseAdapter):
    def fetch(self) -> dict[str, Any]:
        return {"status": "not_configured", "source": "mlb_stats", "pitchers": [], "hitters": []}


class WNBAStatsAdapter(BaseAdapter):
    def fetch(self) -> dict[str, Any]:
        return {"status": "not_configured", "source": "wnba_stats", "teams": []}


class SoccerStatsAdapter(BaseAdapter):
    def fetch(self) -> dict[str, Any]:
        return {"status": "not_configured", "source": "soccer_world_cup", "matches": []}


class WeatherAdapter(BaseAdapter):
    def fetch(self) -> dict[str, Any]:
        return {"status": "not_configured", "source": "weather", "games": []}


class InjuryReportsAdapter(BaseAdapter):
    def fetch(self) -> dict[str, Any]:
        return {"status": "not_configured", "source": "injury_reports", "reports": []}


class ProjectedLineupsAdapter(BaseAdapter):
    def fetch(self) -> dict[str, Any]:
        return {"status": "not_configured", "source": "projected_lineups", "lineups": []}
