from __future__ import annotations

from models import AvoidBet, BetGrade, HitPick, HitRunRbiPick, MoneylineLeg, Parlay, Pick, SettledPick, WorldCupMatchCard


IMG = {
    "arraez": "https://a.espncdn.com/i/headshots/mlb/players/full/39832.png",
    "freeman": "https://a.espncdn.com/i/headshots/mlb/players/full/30193.png",
    "witt": "https://a.espncdn.com/i/headshots/mlb/players/full/4243695.png",
    "betts": "https://a.espncdn.com/i/headshots/mlb/players/full/33039.png",
    "soto": "https://a.espncdn.com/i/headshots/mlb/players/full/36969.png",
    "jram": "https://a.espncdn.com/i/headshots/mlb/players/full/31023.png",
    "yordan": "https://a.espncdn.com/i/headshots/mlb/players/full/36018.png",
    "carroll": "https://a.espncdn.com/i/headshots/mlb/players/full/4240718.png",
    "kirby": "https://a.espncdn.com/i/headshots/mlb/players/full/4198076.png",
    "collier": "https://a.espncdn.com/i/headshots/wnba/players/full/3058915.png",
    "iga": "https://a.espncdn.com/i/headshots/tennis/players/full/4200.png",
    "aces": "https://a.espncdn.com/i/teamlogos/wnba/500/lv.png",
    "dodgers": "https://a.espncdn.com/i/teamlogos/mlb/500/lad.png",
    "mariners": "https://a.espncdn.com/i/teamlogos/mlb/500/sea.png",
    "brazil": "https://flagcdn.com/w320/br.png",
    "spain": "https://flagcdn.com/w320/es.png",
}


def load_top_picks() -> list[Pick]:
    return [
        Pick(sport="MLB", league="MLB", market="Player Hits", selection="Luis Arraez 1+ Hit", matchup="Padres at Rockies", start_time_et="8:40 PM ET", image_url=IMG["arraez"], image_alt="Luis Arraez", grade=BetGrade.A_PLUS, confidence=9.3, probability=78.5, fair_odds=-365, sportsbook_odds=-245, edge=9.7, recommended_stake="1.25u", reasoning="Elite contact profile against a pitch-to-contact righty with low whiff rate.", injury_notes="No injury tag. Confirmed in projected lineup.", weather_notes="Mild wind out to right; no delay risk.", market_movement="Opened -225, still playable to -270.", simulation_support="Supports"),
        Pick(sport="Basketball", league="WNBA", market="Moneyline", selection="Las Vegas Aces ML", matchup="Aces at Sun", start_time_et="7:00 PM ET", image_url=IMG["aces"], image_alt="Las Vegas Aces", grade=BetGrade.A, confidence=8.9, probability=72.0, fair_odds=-257, sportsbook_odds=-210, edge=6.3, recommended_stake="1.0u", reasoning="Pace and half-court efficiency edge with opponent on short rest.", injury_notes="Opponent rotation guard questionable.", weather_notes="Indoor venue.", market_movement="Light favorite money, no chase signal.", simulation_support="Supports"),
        Pick(sport="Soccer", league="FIFA World Cup", market="Double Chance", selection="Brazil or Draw", matchup="Brazil vs Norway", start_time_et="3:00 PM ET", image_url=IMG["brazil"], image_alt="Brazil", grade=BetGrade.A, confidence=8.7, probability=74.2, fair_odds=-287, sportsbook_odds=-230, edge=5.9, recommended_stake="1.0u", reasoning="Elo gap and shot-quality projection favor Brazil avoiding defeat.", injury_notes="No major lineup downgrade in current mock feed.", weather_notes="Neutral conditions.", market_movement="Stable; no steam tax.", simulation_support="Supports"),
        Pick(sport="MLB", league="MLB", market="Team Total", selection="Dodgers Over 4.5 Runs", matchup="Dodgers at Diamondbacks", start_time_et="9:40 PM ET", image_url=IMG["dodgers"], image_alt="Los Angeles Dodgers", grade=BetGrade.A_MINUS, confidence=8.4, probability=61.5, fair_odds=-160, sportsbook_odds=+105, edge=7.9, recommended_stake="0.75u", reasoning="Top-five run environment with bullpen fatigue on the opponent side.", injury_notes="Core bats projected active.", weather_notes="Warm park with carry.", market_movement="Total nudged up half run; still positive at plus money.", simulation_support="Supports"),
        Pick(sport="MLB", league="MLB", market="Player HRR", selection="Mookie Betts 1+ Hit/Run/RBI", matchup="Dodgers at Diamondbacks", start_time_et="9:40 PM ET", image_url=IMG["betts"], image_alt="Mookie Betts", grade=BetGrade.A_MINUS, confidence=8.2, probability=69.0, fair_odds=-223, sportsbook_odds=-175, edge=5.3, recommended_stake="0.75u", reasoning="Leadoff plate volume plus strong implied team total.", injury_notes="No limitations reported.", weather_notes="Positive hitting weather.", market_movement="Minor juice increase.", simulation_support="Supports"),
        Pick(sport="Basketball", league="WNBA", market="Player Points", selection="Napheesa Collier Over 18.5 Points", matchup="Lynx at Liberty", start_time_et="8:00 PM ET", image_url=IMG["collier"], image_alt="Napheesa Collier", grade=BetGrade.B_PLUS, confidence=7.8, probability=59.0, fair_odds=-144, sportsbook_odds=-115, edge=4.7, recommended_stake="0.5u", reasoning="Usage floor remains strong, but number is near fair value.", injury_notes="No injury concern.", weather_notes="Indoor venue.", market_movement="Opened 17.5; reduced stake after move.", simulation_support="Neutral"),
        Pick(sport="Soccer", league="FIFA World Cup", market="Total Goals", selection="Spain vs Japan Under 3.5 Goals", matchup="Spain vs Japan", start_time_et="11:00 AM ET", image_url=IMG["spain"], image_alt="Spain", grade=BetGrade.B_PLUS, confidence=7.6, probability=66.8, fair_odds=-201, sportsbook_odds=-165, edge=4.2, recommended_stake="0.5u", reasoning="Goal distribution leans controlled unless early red card breaks shape.", injury_notes="Expected lineups intact.", weather_notes="Normal pitch conditions.", market_movement="Market agrees; not enough edge for full unit.", simulation_support="Supports"),
        Pick(sport="MLB", league="MLB", market="Strikeouts", selection="George Kirby Over 5.5 Ks", matchup="Mariners vs Athletics", start_time_et="10:10 PM ET", image_url=IMG["kirby"], image_alt="George Kirby", grade=BetGrade.B_PLUS, confidence=7.5, probability=58.2, fair_odds=-139, sportsbook_odds=+105, edge=4.0, recommended_stake="0.5u", reasoning="Opponent chase rate is favorable, but pitch count cap keeps grade down.", injury_notes="No restriction, normal rest.", weather_notes="Pitcher-friendly marine layer.", market_movement="Plus money remains available.", simulation_support="Neutral"),
        Pick(sport="Tennis", league="WTA", market="Moneyline", selection="Iga Swiatek ML", matchup="Swiatek vs Pegula", start_time_et="1:30 PM ET", image_url=IMG["iga"], image_alt="Iga Swiatek", grade=BetGrade.A_MINUS, confidence=8.1, probability=75.0, fair_odds=-300, sportsbook_odds=-250, edge=4.8, recommended_stake="0.75u", reasoning="Return game edge and hold/break model support the favorite.", injury_notes="No reported concern.", weather_notes="Closed roof possible; neutral.", market_movement="Slight move toward favorite.", simulation_support="Supports"),
        Pick(sport="MLB", league="MLB", market="First 5 Innings", selection="Mariners F5 ML", matchup="Mariners vs Athletics", start_time_et="10:10 PM ET", image_url=IMG["mariners"], image_alt="Seattle Mariners", grade=BetGrade.B_PLUS, confidence=7.4, probability=55.6, fair_odds=-125, sportsbook_odds=+110, edge=3.5, recommended_stake="0.4u", reasoning="Starting pitcher edge before bullpen volatility enters.", injury_notes="Lineup has one rest-risk bat.", weather_notes="Neutral.", market_movement="No major movement.", simulation_support="Neutral"),
        Pick(sport="Football", league="NFL", market="Preseason Lean", selection="No Play", matchup="No qualified card", start_time_et="TBD", image_url="https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png", image_alt="NFL", grade=BetGrade.NO_PLAY, confidence=5.0, probability=50.5, fair_odds=-102, sportsbook_odds=-110, edge=-1.4, recommended_stake="0u", reasoning="Mock board rejects thin preseason edges.", injury_notes="Depth chart uncertainty.", weather_notes="Unknown.", market_movement="Public money without confirmation.", simulation_support="Rejects"),
    ]


def load_hit_picks() -> list[HitPick]:
    return [
        HitPick(player="Luis Arraez", team="SD", opponent="COL", start_time_et="8:40 PM ET", image_url=IMG["arraez"], pitcher_matchup="vs RHP Cal Quantrill", handedness_matchup="LHB vs RHP", batting_order_spot=1, recent_form="13 hits over last 7 starts", hit_probability=78.5, confidence=9.3, grade=BetGrade.A_PLUS, reasoning="Contact floor, leadoff volume, and low-strikeout matchup all align."),
        HitPick(player="Freddie Freeman", team="LAD", opponent="ARI", start_time_et="9:40 PM ET", image_url=IMG["freeman"], pitcher_matchup="vs RHP Brandon Pfaadt", handedness_matchup="LHB vs RHP", batting_order_spot=3, recent_form=".381 OBP last 10 games", hit_probability=72.4, confidence=8.6, grade=BetGrade.A, reasoning="Excellent platoon split with multiple RBI-context plate appearances projected."),
        HitPick(player="Bobby Witt Jr.", team="KC", opponent="CHW", start_time_et="7:40 PM ET", image_url=IMG["witt"], pitcher_matchup="vs LHP Ky Bush", handedness_matchup="RHB vs LHP", batting_order_spot=2, recent_form="Hard-hit rate up over two-week sample", hit_probability=69.8, confidence=8.2, grade=BetGrade.A_MINUS, reasoning="Speed adds infield-hit equity and matchup supports early count aggression."),
    ]


def load_hrr_picks() -> list[HitRunRbiPick]:
    return [
        HitRunRbiPick(player="Mookie Betts", team="LAD", opponent="ARI", start_time_et="9:40 PM ET", image_url=IMG["betts"], implied_team_total=5.2, batting_order_spot=1, recent_form="Eight runs created in last week", run_environment="Warm, hitter-friendly, taxed bullpen behind starter", probability=69.0, confidence=8.2, grade=BetGrade.A_MINUS, reasoning="Best blend of plate volume and scoring ecosystem."),
        HitRunRbiPick(player="Juan Soto", team="NYY", opponent="BOS", start_time_et="7:10 PM ET", image_url=IMG["soto"], implied_team_total=4.9, batting_order_spot=2, recent_form="Elite walk plus barrel trend", run_environment="Short porch boosts run/RBI paths", probability=66.5, confidence=8.0, grade=BetGrade.A_MINUS, reasoning="Gets on base often enough to cash without needing a hit."),
        HitRunRbiPick(player="Jose Ramirez", team="CLE", opponent="DET", start_time_et="6:40 PM ET", image_url=IMG["jram"], implied_team_total=4.6, batting_order_spot=3, recent_form="Switch-hitter seeing ball well", run_environment="Neutral park, weak middle relief", probability=64.8, confidence=7.8, grade=BetGrade.B_PLUS, reasoning="RBI and run paths both live from the three-hole."),
        HitRunRbiPick(player="Yordan Alvarez", team="HOU", opponent="SEA", start_time_et="8:10 PM ET", image_url=IMG["yordan"], implied_team_total=4.7, batting_order_spot=4, recent_form="Three extra-base hits in last five", run_environment="Power profile offsets park drag", probability=63.2, confidence=7.6, grade=BetGrade.B_PLUS, reasoning="Lower contact floor, but run production ceiling is strong."),
        HitRunRbiPick(player="Corbin Carroll", team="ARI", opponent="LAD", start_time_et="9:40 PM ET", image_url=IMG["carroll"], implied_team_total=4.2, batting_order_spot=1, recent_form="Stolen-base and run pressure trending up", run_environment="Good pace game, moderate total", probability=61.0, confidence=7.4, grade=BetGrade.B_PLUS, reasoning="Leadoff role supplies enough run and hit paths for a half-unit look."),
    ]


def load_moneyline_parlay() -> Parlay:
    legs = [
        MoneylineLeg(leg="Las Vegas Aces ML", sport="Basketball", league="WNBA", matchup="Aces at Sun", start_time_et="7:00 PM ET", image_url=IMG["aces"], probability=72.0, estimated_odds=-210, reason="Superior offensive rating and rest-adjusted rotation edge."),
        MoneylineLeg(leg="Iga Swiatek ML", sport="Tennis", league="WTA", matchup="Swiatek vs Pegula", start_time_et="1:30 PM ET", image_url=IMG["iga"], probability=75.0, estimated_odds=-250, reason="Return pressure projection creates a high floor."),
        MoneylineLeg(leg="Brazil Draw No Bet", sport="Soccer", league="FIFA World Cup", matchup="Brazil vs Norway", start_time_et="3:00 PM ET", image_url=IMG["brazil"], probability=76.0, estimated_odds=-240, reason="Team-strength model rejects underdog upset pricing."),
        MoneylineLeg(leg="Mariners F5 ML", sport="MLB", league="MLB", matchup="Mariners vs Athletics", start_time_et="10:10 PM ET", image_url=IMG["mariners"], probability=55.6, estimated_odds=+110, reason="Starter edge is strongest before full-game bullpen exposure.", removable_for_safer_card=True),
    ]
    return Parlay(legs=legs, combined_probability=22.9, estimated_odds=+337, risk_rating="Moderate", safer_removes=["Mariners F5 ML"])


def load_world_cup_cards() -> list[WorldCupMatchCard]:
    return [
        WorldCupMatchCard(match="Brazil vs Norway", start_time_et="3:00 PM ET", image_url=IMG["brazil"], legs=["Brazil double chance", "Under 4.5 goals", "Brazil over 3.5 corners"], estimated_odds=+118, estimated_probability=51.0, confidence=7.8, reasoning="Brazil control and Norway's transition-heavy profile keep the combo live without requiring a blowout.", most_likely_score="Brazil 2-1", avoid_list=["Anytime scorer at short juice", "Norway team total over 1.5", "Exact score lottery bets"]),
        WorldCupMatchCard(match="Spain vs Japan", start_time_et="11:00 AM ET", image_url=IMG["spain"], legs=["Spain double chance", "Under 4.5 goals", "Japan under 2.5 goals"], estimated_odds=+106, estimated_probability=52.5, confidence=7.6, reasoning="Possession edge limits Japan chance volume while under 4.5 protects against a 2-1 or 3-1 game.", most_likely_score="Spain 2-1", avoid_list=["Spain -1.5 handicap", "Both teams to score at bad price", "First goalscorer props"]),
    ]


def load_pick_history() -> list[SettledPick]:
    return [
        SettledPick(date="2026-07-04", sport="MLB", league="MLB", selection="Luis Arraez 1+ Hit", odds=-235, stake_units=1.25, result="Win", profit_units=0.53),
        SettledPick(date="2026-07-04", sport="Basketball", league="WNBA", selection="Aces ML", odds=-205, stake_units=1.0, result="Win", profit_units=0.49),
        SettledPick(date="2026-07-04", sport="Soccer", league="FIFA World Cup", selection="Spain/Japan Under 3.5", odds=-160, stake_units=0.5, result="Loss", profit_units=-0.50),
        SettledPick(date="2026-07-03", sport="MLB", league="MLB", selection="Dodgers TT Over 4.5", odds=+102, stake_units=0.75, result="Win", profit_units=0.77),
        SettledPick(date="2026-07-03", sport="Tennis", league="WTA", selection="Iga Swiatek ML", odds=-245, stake_units=0.75, result="Win", profit_units=0.31),
        SettledPick(date="2026-07-02", sport="MLB", league="MLB", selection="Mariners F5 ML", odds=+110, stake_units=0.4, result="Loss", profit_units=-0.40),
        SettledPick(date="2026-07-01", sport="Basketball", league="WNBA", selection="Napheesa Collier Over 18.5", odds=-115, stake_units=0.5, result="Push", profit_units=0.00),
        SettledPick(date="2026-06-29", sport="Soccer", league="FIFA World Cup", selection="Brazil double chance", odds=-225, stake_units=1.0, result="Win", profit_units=0.44),
        SettledPick(date="2026-06-21", sport="MLB", league="MLB", selection="Freddie Freeman 1+ Hit", odds=-250, stake_units=1.0, result="Win", profit_units=0.40),
        SettledPick(date="2026-06-12", sport="MLB", league="MLB", selection="Bobby Witt Jr. 1+ Hit", odds=-210, stake_units=1.0, result="Loss", profit_units=-1.00),
        SettledPick(date="2026-05-30", sport="Basketball", league="WNBA", selection="Aces ML", odds=-190, stake_units=1.0, result="Win", profit_units=0.53),
        SettledPick(date="2026-04-18", sport="Tennis", league="WTA", selection="Iga Swiatek ML", odds=-260, stake_units=0.75, result="Win", profit_units=0.29),
        SettledPick(date="2025-12-30", sport="MLB", league="MLB", selection="Archive sample MLB edge", odds=+115, stake_units=0.5, result="Loss", profit_units=-0.50),
    ]


def load_avoid_bets() -> list[AvoidBet]:
    return [
        AvoidBet(bet="Dodgers full-game ML", sport="MLB", league="MLB", matchup="Dodgers at Diamondbacks", market="Moneyline", sportsbook_odds=-285, start_time_et="9:40 PM ET", image_url=IMG["dodgers"], category="Overpriced favorite", risk="High", reason="Our mock fair line is closer to -230. Full-game bullpen variance makes -285 too expensive when the stronger edge is Dodgers team total over 4.5."),
        AvoidBet(bet="Napheesa Collier Over 22.5 Points", sport="Basketball", league="WNBA", matchup="Lynx at Liberty", market="Player points", sportsbook_odds=-120, start_time_et="8:00 PM ET", image_url=IMG["collier"], category="Bad number", risk="High", reason="The playable number was 18.5 at smaller stake. At 22.5 the projection loses its cushion and needs a ceiling game against a slower Liberty defensive shell."),
        AvoidBet(bet="Brazil ML + Over 2.5 Goals + Haaland anytime scorer", sport="Soccer", league="FIFA World Cup", matchup="Brazil vs Norway", market="Same-game parlay", sportsbook_odds=+220, start_time_et="3:00 PM ET", image_url=IMG["brazil"], category="Public-heavy trap", risk="Extreme", reason="The legs look flashy, but this asks Brazil to win, the match to open up, and Norway's highest-taxed scorer to convert. Brazil double chance or draw no bet is the disciplined angle."),
        AvoidBet(bet="Corbin Carroll 1+ Hit", sport="MLB", league="MLB", matchup="Diamondbacks vs Dodgers", market="Player hits", sportsbook_odds=-190, start_time_et="9:40 PM ET", image_url=IMG["carroll"], category="Bad odds", risk="Medium", reason="Carroll is viable for hit/run/RBI because of multiple paths, but straight 1+ hit at -190 is too rich against a stronger Dodgers pitching setup."),
        AvoidBet(bet="George Kirby Over 6.5 Strikeouts", sport="MLB", league="MLB", matchup="Mariners vs Athletics", market="Pitcher strikeouts", sportsbook_odds=+115, start_time_et="10:10 PM ET", image_url=IMG["kirby"], category="Volatile prop", risk="High", reason="We only grade over 5.5 as a lean. Moving to 6.5 adds pitch-count and efficiency risk without enough plus-money compensation."),
        AvoidBet(bet="Spain -1.5 goals handicap", sport="Soccer", league="FIFA World Cup", matchup="Spain vs Japan", market="Spread", sportsbook_odds=+135, start_time_et="11:00 AM ET", image_url=IMG["spain"], category="Mismatch with simulation", risk="High", reason="The simulation likes Spain avoiding defeat and under 4.5, not a margin chase. Japan's compact block makes a one-goal Spain win live."),
    ]
