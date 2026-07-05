# Prop Plug Pat — Elite Betting Board

A premium Streamlit sports betting dashboard with mock data, ranked picks, simulation outputs, CSV export, and modular source adapters ready for real APIs.

## What is included

- Top 10 best bets ranked by grade, confidence, probability, and edge
- Sport and league tabs for MLB, WNBA, FIFA World Cup, WTA/Tennis, parlays, simulations, avoid plays, and tracker
- Player/team images and listed ET start times on pick cards
- Best MLB 1+ hit picks
- Best MLB 1+ hit/run/RBI picks
- High-confidence moneyline parlay builder
- FIFA World Cup match-card parlays
- Specific do-not-bet plays with matchup, odds, start time, trap type, and pass reason
- Pick tracker for all-time, yearly, monthly, weekly, and yesterday's unit P/L
- Linked Sports Betting AI Chatbot page for best bets, avoid plays, parlays, staking, MLB props, and tracker questions
- Mock MLB, soccer, and WNBA simulation module
- API adapter placeholders for odds, MLB, WNBA, soccer, weather, injuries, and lineups
- Eastern Time refresh schedule for 9am, 12pm, 2pm, 6pm, and 7pm
- Manual refresh and CSV export
- Mobile-friendly Streamlit layout

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

Open the local URL Streamlit prints in your terminal.

## Project structure

```text
app.py
assets/
data/
models/
services/
simulations/
utils/
README.md
requirements.txt
.env.example
```

## Plugging in real data

Replace the mock methods in `services/adapters.py` with requests to your chosen providers. Keep the return shapes normalized, then map those normalized results into the Pydantic models in `models/schemas.py`.

Recommended integration order:

1. Odds API
2. Projected lineups
3. Injury reports
4. MLB stats
5. Weather
6. WNBA stats
7. Soccer and World Cup stats

The app intentionally does not force weak picks. If a real feed returns too few qualified plays, show `No Play` rather than filling a card with thin edges.

## Streamlit Community Cloud deployment

1. Push this project to a GitHub repository.
2. Go to Streamlit Community Cloud and create a new app.
3. Select the repository, branch, and `app.py` as the entrypoint.
4. Add API keys in the app's Secrets settings using the names from `.env.example`.
5. Deploy.

For Streamlit secrets, use this shape:

```toml
ODDS_API_KEY = "your-key"
MLB_STATS_API_KEY = "your-key"
WNBA_STATS_API_KEY = "your-key"
SOCCER_STATS_API_KEY = "your-key"
WEATHER_API_KEY = "your-key"
INJURY_REPORTS_API_KEY = "your-key"
LINEUPS_API_KEY = "your-key"
APP_TIMEZONE = "America/New_York"
```

## Disclaimer

This app is for analysis and entertainment, not guaranteed outcomes. Gamble responsibly, keep bankroll rules firm, and never wager more than you can afford to lose.
