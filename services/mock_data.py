from __future__ import annotations

from models import AvoidBet, BetGrade, HitPick, HitRunRbiPick, MoneylineLeg, Parlay, Pick, WorldCupMatchCard


def load_top_picks() -> list[Pick]:
    return [
        Pick(sport="MLB", market="Player Hits", selection="Luis Arraez 1+ Hit", grade=BetGrade.A_PLUS, confidence=9.3, probability=78.5, fair_odds=-365, sportsbook_odds=-245, edge=9.7, recommended_stake="1.25u", reasoning="Elite contact profile against a pitch-to-contact righty with low whiff rate.", injury_notes="No injury tag. Confirmed in projected lineup.", weather_notes="Mild wind out to right; no delay risk.", market_movement="Opened -225, still playable to -270.", simulation_support="Supports"),
        Pick(sport="WNBA", market="Moneyline", selection="Las Vegas Aces ML", grade=BetGrade.A, confidence=8.9, probability=72.0, fair_odds=-257, sportsbook_odds=-210, edge=6.3, recommended_stake="1.0u", reasoning="Pace and half-court efficiency edge with opponent on short rest.", injury_notes="Opponent rotation guard questionable.", weather_notes="Indoor venue.", market_movement="Light favorite money, no chase signal.", simulation_support="Supports"),
        Pick(sport="Soccer", market="Double Chance", selection="Brazil or Draw", grade=BetGrade.A, confidence=8.7, probability=74.2, fair_odds=-287, sportsbook_odds=-230, edge=5.9, recommended_stake="1.0u", reasoning="Elo gap and shot-quality projection favor Brazil avoiding defeat.", injury_notes="No major lineup downgrade in current mock feed.", weather_notes="Neutral conditions.", market_movement="Stable; no steam tax.", simulation_support="Supports"),
        Pick(sport="MLB", market="Team Total", selection="Dodgers Over 4.5 Runs", grade=BetGrade.A_MINUS, confidence=8.4, probability=61.5, fair_odds=-160, sportsbook_odds=+105, edge=7.9, recommended_stake="0.75u", reasoning="Top-five run environment with bullpen fatigue on the opponent side.", injury_notes="Core bats projected active.", weather_notes="Warm park with carry.", market_movement="Total nudged up half run; still positive at plus money.", simulation_support="Supports"),
        Pick(sport="MLB", market="Player HRR", selection="Mookie Betts 1+ Hit/Run/RBI", grade=BetGrade.A_MINUS, confidence=8.2, probability=69.0, fair_odds=-223, sportsbook_odds=-175, edge=5.3, recommended_stake="0.75u", reasoning="Leadoff plate volume plus strong implied team total.", injury_notes="No limitations reported.", weather_notes="Positive hitting weather.", market_movement="Minor juice increase.", simulation_support="Supports"),
        Pick(sport="WNBA", market="Player Points", selection="Napheesa Collier Over 18.5 Points", grade=BetGrade.B_PLUS, confidence=7.8, probability=59.0, fair_odds=-144, sportsbook_odds=-115, edge=4.7, recommended_stake="0.5u", reasoning="Usage floor remains strong, but number is near fair value.", injury_notes="No injury concern.", weather_notes="Indoor venue.", market_movement="Opened 17.5; reduced stake after move.", simulation_support="Neutral"),
        Pick(sport="Soccer", market="Total Goals", selection="Spain vs Japan Under 3.5 Goals", grade=BetGrade.B_PLUS, confidence=7.6, probability=66.8, fair_odds=-201, sportsbook_odds=-165, edge=4.2, recommended_stake="0.5u", reasoning="Goal distribution leans controlled unless early red card breaks shape.", injury_notes="Expected lineups intact.", weather_notes="Normal pitch conditions.", market_movement="Market agrees; not enough edge for full unit.", simulation_support="Supports"),
        Pick(sport="MLB", market="Strikeouts", selection="George Kirby Over 5.5 Ks", grade=BetGrade.B_PLUS, confidence=7.5, probability=58.2, fair_odds=-139, sportsbook_odds=+105, edge=4.0, recommended_stake="0.5u", reasoning="Opponent chase rate is favorable, but pitch count cap keeps grade down.", injury_notes="No restriction, normal rest.", weather_notes="Pitcher-friendly marine layer.", market_movement="Plus money remains available.", simulation_support="Neutral"),
        Pick(sport="Tennis", market="Moneyline", selection="Iga Swiatek ML", grade=BetGrade.A_MINUS, confidence=8.1, probability=75.0, fair_odds=-300, sportsbook_odds=-250, edge=4.8, recommended_stake="0.75u", reasoning="Return game edge and hold/break model support the favorite.", injury_notes="No reported concern.", weather_notes="Closed roof possible; neutral.", market_movement="Slight move toward favorite.", simulation_support="Supports"),
        Pick(sport="MLB", market="First 5 Innings", selection="Mariners F5 ML", grade=BetGrade.B_PLUS, confidence=7.4, probability=55.6, fair_odds=-125, sportsbook_odds=+110, edge=3.5, recommended_stake="0.4u", reasoning="Starting pitcher edge before bullpen volatility enters.", injury_notes="Lineup has one rest-risk bat.", weather_notes="Neutral.", market_movement="No major movement.", simulation_support="Neutral"),
        Pick(sport="NFL", market="Preseason Lean", selection="No Play", grade=BetGrade.NO_PLAY, confidence=5.0, probability=50.5, fair_odds=-102, sportsbook_odds=-110, edge=-1.4, recommended_stake="0u", reasoning="Mock board rejects thin preseason edges.", injury_notes="Depth chart uncertainty.", weather_notes="Unknown.", market_movement="Public money without confirmation.", simulation_support="Rejects"),
    ]


def load_hit_picks() -> list[HitPick]:
    return [
        HitPick(player="Luis Arraez", team="SD", opponent="COL", pitcher_matchup="vs RHP Cal Quantrill", handedness_matchup="LHB vs RHP", batting_order_spot=1, recent_form="13 hits over last 7 starts", hit_probability=78.5, confidence=9.3, grade=BetGrade.A_PLUS, reasoning="Contact floor, leadoff volume, and low-strikeout matchup all align."),
        HitPick(player="Freddie Freeman", team="LAD", opponent="ARI", pitcher_matchup="vs RHP Brandon Pfaadt", handedness_matchup="LHB vs RHP", batting_order_spot=3, recent_form=".381 OBP last 10 games", hit_probability=72.4, confidence=8.6, grade=BetGrade.A, reasoning="Excellent platoon split with multiple RBI-context plate appearances projected."),
        HitPick(player="Bobby Witt Jr.", team="KC", opponent="CHW", pitcher_matchup="vs LHP Ky Bush", handedness_matchup="RHB vs LHP", batting_order_spot=2, recent_form="Hard-hit rate up over two-week sample", hit_probability=69.8, confidence=8.2, grade=BetGrade.A_MINUS, reasoning="Speed adds infield-hit equity and matchup supports early count aggression."),
    ]


def load_hrr_picks() -> list[HitRunRbiPick]:
    return [
        HitRunRbiPick(player="Mookie Betts", team="LAD", opponent="ARI", implied_team_total=5.2, batting_order_spot=1, recent_form="Eight runs created in last week", run_environment="Warm, hitter-friendly, taxed bullpen behind starter", probability=69.0, confidence=8.2, grade=BetGrade.A_MINUS, reasoning="Best blend of plate volume and scoring ecosystem."),
        HitRunRbiPick(player="Juan Soto", team="NYY", opponent="BOS", implied_team_total=4.9, batting_order_spot=2, recent_form="Elite walk plus barrel trend", run_environment="Short porch boosts run/RBI paths", probability=66.5, confidence=8.0, grade=BetGrade.A_MINUS, reasoning="Gets on base often enough to cash without needing a hit."),
        HitRunRbiPick(player="Jose Ramirez", team="CLE", opponent="DET", implied_team_total=4.6, batting_order_spot=3, recent_form="Switch-hitter seeing ball well", run_environment="Neutral park, weak middle relief", probability=64.8, confidence=7.8, grade=BetGrade.B_PLUS, reasoning="RBI and run paths both live from the three-hole."),
        HitRunRbiPick(player="Yordan Alvarez", team="HOU", opponent="SEA", implied_team_total=4.7, batting_order_spot=4, recent_form="Three extra-base hits in last five", run_environment="Power profile offsets park drag", probability=63.2, confidence=7.6, grade=BetGrade.B_PLUS, reasoning="Lower contact floor, but run production ceiling is strong."),
        HitRunRbiPick(player="Corbin Carroll", team="ARI", opponent="LAD", implied_team_total=4.2, batting_order_spot=1, recent_form="Stolen-base and run pressure trending up", run_environment="Good pace game, moderate total", probability=61.0, confidence=7.4, grade=BetGrade.B_PLUS, reasoning="Leadoff role supplies enough run and hit paths for a half-unit look."),
    ]


def load_moneyline_parlay() -> Parlay:
    legs = [
        MoneylineLeg(leg="Las Vegas Aces ML", sport="WNBA", probability=72.0, estimated_odds=-210, reason="Superior offensive rating and rest-adjusted rotation edge."),
        MoneylineLeg(leg="Iga Swiatek ML", sport="Tennis", probability=75.0, estimated_odds=-250, reason="Return pressure projection creates a high floor."),
        MoneylineLeg(leg="Brazil Draw No Bet", sport="Soccer", probability=76.0, estimated_odds=-240, reason="Team-strength model rejects underdog upset pricing."),
        MoneylineLeg(leg="Mariners F5 ML", sport="MLB", probability=55.6, estimated_odds=+110, reason="Starter edge is strongest before full-game bullpen exposure.", removable_for_safer_card=True),
    ]
    return Parlay(legs=legs, combined_probability=22.9, estimated_odds=+337, risk_rating="Moderate", safer_removes=["Mariners F5 ML"])


def load_world_cup_cards() -> list[WorldCupMatchCard]:
    return [
        WorldCupMatchCard(match="Brazil vs Croatia", legs=["Brazil double chance", "Under 4.5 goals", "Brazil over 3.5 corners"], estimated_odds=+118, estimated_probability=51.0, confidence=7.8, reasoning="Brazil control plus Croatia's lower tempo keeps the combo correlated without requiring a blowout.", most_likely_score="Brazil 2-0", avoid_list=["Anytime scorer at short juice", "Croatia team total over 1.5", "Exact score lottery bets"]),
        WorldCupMatchCard(match="Spain vs Japan", legs=["Spain double chance", "Under 4.5 goals", "Japan under 2.5 goals"], estimated_odds=+106, estimated_probability=52.5, confidence=7.6, reasoning="Possession edge limits Japan chance volume while under 4.5 protects against a 2-1 or 3-1 game.", most_likely_score="Spain 2-1", avoid_list=["Spain -1.5 handicap", "Both teams to score at bad price", "First goalscorer props"]),
    ]


def load_avoid_bets() -> list[AvoidBet]:
    return [
        AvoidBet(bet="Heavy MLB favorite full-game ML above -260", category="Overpriced favorite", risk="High", reason="Bullpen variance makes the price too thin unless tied to a parlay hedge plan."),
        AvoidBet(bet="WNBA star points overs after injury-questionable tag", category="Injury risk", risk="Extreme", reason="Usage and minutes can collapse even if the player is active."),
        AvoidBet(bet="Public World Cup same-game parlay with favorite ML, over, and star scorer", category="Public-heavy trap", risk="High", reason="Correlation is weaker than the ticket suggests and books shade these combos hard."),
        AvoidBet(bet="MLB hits props for confirmed bottom-third hitters at -180 or worse", category="Bad odds", risk="Medium", reason="Plate appearance volume is not strong enough to justify premium juice."),
        AvoidBet(bet="Volatile pitcher strikeout overs with weather delay risk", category="Volatile props", risk="High", reason="Delay risk can shorten starts and erase otherwise sound K projections."),
    ]
