from __future__ import annotations

import socket
import subprocess
import sys
from datetime import datetime, timedelta
from html import escape
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from services.mock_data import (
    load_avoid_bets,
    load_hit_picks,
    load_hrr_picks,
    load_moneyline_parlay,
    load_pick_history,
    load_top_picks,
    load_world_cup_cards,
)
from simulations import run_all_simulations
from utils import export_board_rows, get_next_refresh_time, grade_badge_class, rank_picks


st.set_page_config(
    page_title="Prop Plug Pat — Elite Betting Board",
    page_icon="PP",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #050508;
            --panel: rgba(22, 18, 34, 0.76);
            --panel-strong: rgba(33, 25, 50, 0.88);
            --border: rgba(177, 108, 255, 0.24);
            --text: #f6f1ff;
            --muted: #b8acc8;
            --purple: #a855f7;
            --violet: #7c3aed;
            --cyan: #38f8ff;
            --green: #67f5a2;
            --gold: #ffd166;
            --red: #ff5c8a;
        }
        .stApp {
            color: var(--text);
            background:
                radial-gradient(circle at 20% 0%, rgba(124, 58, 237, 0.26), transparent 34%),
                radial-gradient(circle at 88% 12%, rgba(56, 248, 255, 0.13), transparent 32%),
                linear-gradient(180deg, #050508 0%, #090711 55%, #050508 100%);
        }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stToolbar"] { right: 1rem; }
        h1, h2, h3 { letter-spacing: 0; }
        h1 {
            font-size: clamp(2.1rem, 5vw, 4.8rem);
            line-height: 0.95;
            margin-bottom: 0.4rem;
            color: #fff;
            text-shadow: 0 0 32px rgba(168, 85, 247, 0.5);
        }
        h2 { margin-top: 1.6rem; }
        .hero {
            padding: 1.3rem 0 0.8rem 0;
            border-bottom: 1px solid rgba(168, 85, 247, 0.22);
            margin-bottom: 1rem;
        }
        .eyebrow {
            color: var(--cyan);
            font-size: 0.78rem;
            letter-spacing: 0.18rem;
            text-transform: uppercase;
            font-weight: 800;
        }
        .subtle { color: var(--muted); }
        .glass {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.09), rgba(255, 255, 255, 0.035));
            border: 1px solid var(--border);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(14px);
            border-radius: 8px;
            padding: 1rem;
        }
        .metric-card {
            min-height: 112px;
        }
        .metric-label {
            color: var(--muted);
            font-size: 0.78rem;
            text-transform: uppercase;
            font-weight: 800;
            letter-spacing: 0.08rem;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 900;
            margin-top: 0.15rem;
        }
        .pick-card {
            margin: 0.65rem 0;
            position: relative;
            overflow: hidden;
        }
        .pick-layout {
            display: grid;
            grid-template-columns: 112px minmax(0, 1fr);
            gap: 1rem;
            align-items: start;
        }
        .pick-image {
            width: 112px;
            height: 112px;
            border-radius: 8px;
            object-fit: contain;
            background: rgba(0, 0, 0, 0.32);
            border: 1px solid rgba(255, 255, 255, 0.12);
            padding: 0.35rem;
        }
        .pick-card:before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(var(--cyan), var(--purple));
        }
        .rank {
            width: 42px;
            height: 42px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            background: rgba(168, 85, 247, 0.18);
            border: 1px solid rgba(168, 85, 247, 0.5);
            color: #fff;
            font-weight: 900;
            margin-right: 0.75rem;
        }
        .badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            padding: 0.22rem 0.58rem;
            font-size: 0.76rem;
            font-weight: 900;
            margin: 0.15rem 0.25rem 0.15rem 0;
            border: 1px solid rgba(255,255,255,0.14);
        }
        .time-badge {
            background: rgba(56, 248, 255, 0.11);
            color: #dffeff;
        }
        .grade-aplus { background: rgba(103, 245, 162, 0.18); color: var(--green); }
        .grade-a { background: rgba(56, 248, 255, 0.15); color: var(--cyan); }
        .grade-aminus { background: rgba(255, 209, 102, 0.15); color: var(--gold); }
        .grade-bplus { background: rgba(168, 85, 247, 0.18); color: #d9b4ff; }
        .grade-no-play { background: rgba(255, 92, 138, 0.14); color: var(--red); }
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.55rem;
            margin-top: 0.8rem;
        }
        .stat {
            background: rgba(0, 0, 0, 0.23);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 0.55rem;
        }
        .stat span {
            display: block;
            color: var(--muted);
            font-size: 0.72rem;
            text-transform: uppercase;
            font-weight: 800;
        }
        .stat strong {
            display: block;
            font-size: 1rem;
            margin-top: 0.18rem;
        }
        .mini-title {
            font-weight: 900;
            font-size: 1.05rem;
            margin-bottom: 0.2rem;
        }
        .divider {
            height: 1px;
            background: rgba(255, 255, 255, 0.08);
            margin: 0.8rem 0;
        }
        .tracker-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.7rem;
            margin: 0.8rem 0 1rem;
        }
        .positive { color: var(--green); }
        .negative { color: var(--red); }
        .neutral { color: var(--muted); }
        div[data-testid="stTabs"] button {
            font-weight: 800;
        }
        .no-play {
            border-color: rgba(255, 92, 138, 0.34);
            background: rgba(255, 92, 138, 0.08);
        }
        .stButton > button, .stDownloadButton > button {
            background: linear-gradient(135deg, var(--violet), var(--purple));
            color: white;
            border: 1px solid rgba(255,255,255,0.16);
            border-radius: 8px;
            font-weight: 800;
            min-height: 2.7rem;
        }
        .stDataFrame, [data-testid="stDataFrame"] {
            border: 1px solid rgba(168, 85, 247, 0.25);
            border-radius: 8px;
            overflow: hidden;
        }
        @media (max-width: 780px) {
            .stat-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .tracker-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .pick-layout { grid-template-columns: 72px minmax(0, 1fr); gap: 0.7rem; }
            .pick-image { width: 72px; height: 72px; }
            .rank { width: 34px; height: 34px; }
            .glass { padding: 0.85rem; }
            h1 { font-size: 2.3rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def scheduled_refresh() -> None:
    eastern = ZoneInfo("America/New_York")
    now = datetime.now(eastern)
    next_refresh = get_next_refresh_time(now)
    seconds_until = max(60, int((next_refresh - now).total_seconds()))
    st_autorefresh(interval=seconds_until * 1000, key="scheduled_board_refresh")


def fmt_odds(odds: int) -> str:
    return f"+{odds}" if odds > 0 else str(odds)


def fmt_et(dt: datetime) -> str:
    return dt.strftime("%I:%M %p ET").lstrip("0")


def safe(value: object) -> str:
    return escape(str(value), quote=True)


def fallback_image(label: str) -> str:
    return f"https://ui-avatars.com/api/?name={quote(label)}&background=161222&color=f6f1ff&bold=true&size=256"


def image_tag(src: str, alt: str) -> str:
    fallback = fallback_image(alt)
    return (
        f'<img class="pick-image" src="{safe(src)}" alt="{safe(alt)}" '
        f'onerror="this.onerror=null;this.src=\'{safe(fallback)}\';">'
    )


def card_metric(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="glass metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="subtle">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


DUEL_PORT = 8008


def duel_server_running(port: int = DUEL_PORT) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.25):
            return True
    except OSError:
        return False


def get_lan_url(port: int = DUEL_PORT) -> str | None:
    try:
        host = socket.gethostbyname(socket.gethostname())
    except OSError:
        return None
    if not host or host.startswith("127."):
        return None
    return f"http://{host}:{port}"


def start_duel_server(port: int = DUEL_PORT) -> tuple[bool, str]:
    if duel_server_running(port):
        return True, "Duel server is already running."

    root = Path(__file__).resolve().parent
    log_path = root / "duel_server.log"
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "duel_server:app",
        "--host",
        "0.0.0.0",
        "--port",
        str(port),
    ]
    try:
        log_file = log_path.open("a", encoding="utf-8")
        kwargs = {"cwd": root, "stdout": log_file, "stderr": subprocess.STDOUT}
        if sys.platform.startswith("win"):
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        subprocess.Popen(command, **kwargs)
    except Exception as exc:
        return False, f"Could not start duel server: {exc}"

    for _ in range(12):
        if duel_server_running(port):
            return True, "Duel server started."
    return False, f"Duel server did not answer yet. Check {log_path.name}."


def render_duel_simulator_launcher() -> None:
    local_url = f"http://127.0.0.1:{DUEL_PORT}"
    lan_url = get_lan_url(DUEL_PORT)
    running = duel_server_running(DUEL_PORT)
    status = "Online" if running else "Stopped"
    status_class = "grade-aplus" if running else "grade-no-play"

    st.markdown(
        f"""
        <div class="glass pick-card">
            <div class="mini-title">Manual Yu-Gi-Oh Duel Simulator</div>
            <span class="badge {status_class}">{status}</span>
            <span class="badge">Rooms</span>
            <span class="badge">Bots</span>
            <span class="badge">Local card image cache</span>
            <p class="subtle">Manual table, unrestricted card movement, preset decks, simple bot turns, room links, chat, LP, phases, graveyard, banished, extra deck, and card search.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns([1, 1, 1, 1])
    with cols[0]:
        if st.button("Start Duel Server", use_container_width=True):
            ok, message = start_duel_server(DUEL_PORT)
            if ok:
                st.success(message)
            else:
                st.error(message)
    with cols[1]:
        st.link_button("Open Duel Table", local_url, use_container_width=True)
    with cols[2]:
        st.code(local_url, language=None)
    with cols[3]:
        st.code(lan_url or "LAN URL unavailable", language=None)


def render_pick_card(index: int, pick) -> None:
    grade_class = grade_badge_class(pick.grade.value)
    st.markdown(
        f"""
        <div class="glass pick-card">
            <div class="pick-layout">
                <div>{image_tag(pick.image_url, pick.image_alt)}</div>
                <div>
                    <div>
                        <span class="rank">{index}</span>
                        <span class="mini-title">{safe(pick.selection)}</span>
                    </div>
                    <div>
                        <span class="badge {grade_class}">{pick.grade.value}</span>
                        <span class="badge">{safe(pick.league)}</span>
                        <span class="badge">{safe(pick.market)}</span>
                        <span class="badge time-badge">{safe(pick.start_time_et)}</span>
                        <span class="badge">{safe(pick.simulation_support)}</span>
                    </div>
                    <p class="subtle"><strong>Matchup:</strong> {safe(pick.matchup)}</p>
                    <div class="stat-grid">
                        <div class="stat"><span>Confidence</span><strong>{pick.confidence:.1f}/10</strong></div>
                        <div class="stat"><span>Probability</span><strong>{pick.probability:.1f}%</strong></div>
                        <div class="stat"><span>Fair Odds</span><strong>{fmt_odds(pick.fair_odds)}</strong></div>
                        <div class="stat"><span>Book Odds</span><strong>{fmt_odds(pick.sportsbook_odds)}</strong></div>
                        <div class="stat"><span>Edge</span><strong>{pick.edge:.1f}%</strong></div>
                    </div>
                    <div class="divider"></div>
                    <p><strong>Stake:</strong> {safe(pick.recommended_stake)}</p>
                    <p><strong>Why:</strong> {safe(pick.reasoning)}</p>
                    <p class="subtle"><strong>Injury/lineup:</strong> {safe(pick.injury_notes)}</p>
                    <p class="subtle"><strong>Weather:</strong> {safe(pick.weather_notes)}</p>
                    <p class="subtle"><strong>Market:</strong> {safe(pick.market_movement)}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_score_plot(picks: list) -> None:
    score_df = pd.DataFrame(
        [{"Selection": p.selection, "Confidence": p.confidence, "Probability": p.probability, "Edge": p.edge, "Grade": p.grade.value} for p in picks]
    )
    if score_df.empty:
        return
    fig = px.scatter(
        score_df,
        x="Probability",
        y="Edge",
        size="Confidence",
        color="Grade",
        hover_name="Selection",
        color_discrete_map={"A+": "#67f5a2", "A": "#38f8ff", "A-": "#ffd166", "B+": "#a855f7"},
        size_max=34,
    )
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=360, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)


def render_leaderboard(title: str, picks: list) -> None:
    st.subheader(title)
    if not picks:
        st.markdown('<div class="glass no-play"><strong>No Play</strong><br>No high-confidence plays met the threshold for this league.</div>', unsafe_allow_html=True)
        return
    render_score_plot(picks)
    for index, pick in enumerate(picks, start=1):
        render_pick_card(index, pick)


def render_hit_table(title: str, rows: list, probability_key: str) -> None:
    st.subheader(title)
    if not rows:
        st.markdown('<div class="glass no-play"><strong>No Play</strong><br>No high-confidence plays met the threshold.</div>', unsafe_allow_html=True)
        return
    for row in rows:
        probability = getattr(row, probability_key)
        grade_class = grade_badge_class(row.grade.value)
        st.markdown(
            f"""
            <div class="glass pick-card">
                <div class="pick-layout">
                    <div>{image_tag(row.image_url, row.player)}</div>
                    <div>
                        <div class="mini-title">{safe(row.player)}</div>
                        <span class="badge {grade_class}">{row.grade.value}</span>
                        <span class="badge">{safe(row.team)} vs {safe(row.opponent)}</span>
                        <span class="badge time-badge">{safe(row.start_time_et)}</span>
                        <span class="badge">{probability:.1f}%</span>
                        <p>{safe(row.reasoning)}</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    df = pd.DataFrame([row.model_dump() for row in rows])
    df["grade"] = df["grade"].apply(lambda item: item.value if hasattr(item, "value") else item)
    st.dataframe(df, use_container_width=True, hide_index=True)
    fig = px.bar(
        df,
        x="player",
        y=probability_key,
        color="grade",
        color_discrete_map={"A+": "#67f5a2", "A": "#38f8ff", "A-": "#ffd166", "B+": "#a855f7"},
        text=probability_key,
    )
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=310, margin=dict(l=20, r=20, t=20, b=20))
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


def render_moneyline_parlay() -> None:
    parlay = load_moneyline_parlay()
    st.subheader("Best Moneyline Parlay Across All Sports")
    if not parlay.legs:
        st.markdown('<div class="glass no-play"><strong>No Play</strong><br>No moneyline card met the strict confidence threshold.</div>', unsafe_allow_html=True)
        return
    left, right = st.columns([1.2, 0.8])
    with left:
        for leg in parlay.legs:
            remove = "Safer-card remove" if leg.removable_for_safer_card else "Core leg"
            st.markdown(
                f"""
                <div class="glass pick-card">
                    <div class="pick-layout">
                        <div>{image_tag(leg.image_url, leg.leg)}</div>
                        <div>
                            <div class="mini-title">{safe(leg.leg)}</div>
                            <span class="badge">{safe(leg.league)}</span>
                            <span class="badge time-badge">{safe(leg.start_time_et)}</span>
                            <span class="badge">{leg.probability:.1f}%</span>
                            <span class="badge">{fmt_odds(leg.estimated_odds)}</span>
                            <span class="badge">{remove}</span>
                            <p class="subtle"><strong>Matchup:</strong> {safe(leg.matchup)}</p>
                            <p>{safe(leg.reason)}</p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with right:
        card_metric("Combined Probability", f"{parlay.combined_probability:.1f}%", "Strict threshold legs only")
        card_metric("Estimated Odds", fmt_odds(parlay.estimated_odds), f"Risk: {parlay.risk_rating}")
        st.markdown('<div class="glass"><strong>Legs to remove for safer card</strong><br>' + ", ".join(parlay.safer_removes) + "</div>", unsafe_allow_html=True)


def render_world_cup_cards() -> None:
    st.subheader("FIFA World Cup Match Cards")
    cards = load_world_cup_cards()
    if not cards:
        st.markdown('<div class="glass no-play"><strong>No Play</strong><br>No World Cup matches scheduled today in the current data feed.</div>', unsafe_allow_html=True)
        return
    for card in cards:
        st.markdown(
            f"""
            <div class="glass pick-card">
                <div class="pick-layout">
                    <div>{image_tag(card.image_url, card.match)}</div>
                    <div>
                        <div class="mini-title">{safe(card.match)}</div>
                        <span class="badge time-badge">{safe(card.start_time_et)}</span>
                        <span class="badge">Odds {fmt_odds(card.estimated_odds)}</span>
                        <span class="badge">{card.estimated_probability:.1f}%</span>
                        <span class="badge">Confidence {card.confidence:.1f}/10</span>
                        <p><strong>Legs:</strong> {safe(" | ".join(card.legs))}</p>
                        <p><strong>Most likely score:</strong> {safe(card.most_likely_score)}</p>
                        <p>{safe(card.reasoning)}</p>
                        <p class="subtle"><strong>Avoid:</strong> {safe(", ".join(card.avoid_list))}</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_avoid_bets() -> None:
    st.subheader("Do Not Bet - Specific Plays to Avoid")
    for item in load_avoid_bets():
        st.markdown(
            f"""
            <div class="glass no-play pick-card">
                <div class="pick-layout">
                    <div>{image_tag(item.image_url, item.bet)}</div>
                    <div>
                        <div class="mini-title">{safe(item.bet)}</div>
                        <span class="badge grade-no-play">{safe(item.risk)}</span>
                        <span class="badge">{safe(item.league)}</span>
                        <span class="badge">{safe(item.market)}</span>
                        <span class="badge">{fmt_odds(item.sportsbook_odds)}</span>
                        <span class="badge time-badge">{safe(item.start_time_et)}</span>
                        <p class="subtle"><strong>Matchup:</strong> {safe(item.matchup)}</p>
                        <p><strong>Why pass:</strong> {safe(item.reason)}</p>
                        <p class="subtle"><strong>Trap type:</strong> {safe(item.category)}</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_simulations() -> None:
    st.subheader("Simulation Module")
    sims = run_all_simulations()
    tabs = st.tabs([sim.sport for sim in sims])
    for tab, sim in zip(tabs, sims):
        with tab:
            left, right = st.columns([0.9, 1.1])
            with left:
                st.markdown(
                    f"""
                    <div class="glass">
                        <div class="mini-title">{sim.matchup}</div>
                        <p><strong>Projected score:</strong> {sim.projected_score}</p>
                        <p><strong>Bet probability:</strong> {sim.bet_probability:.1f}%</p>
                        <p><strong>Confidence:</strong> {sim.confidence_rating:.1f}/10</p>
                        <span class="badge">{sim.verdict}</span>
                        <div class="divider"></div>
                        <p><strong>Most likely outcomes:</strong> {", ".join(sim.most_likely_outcomes)}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with right:
                fig = go.Figure(data=[go.Pie(labels=list(sim.probability_distribution.keys()), values=list(sim.probability_distribution.values()), hole=0.55)])
                fig.update_traces(marker=dict(colors=["#a855f7", "#38f8ff", "#ffd166", "#ff5c8a"]))
                fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=320, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)


def format_units(value: float) -> str:
    prefix = "+" if value > 0 else ""
    return f"{prefix}{value:.2f}u"


def unit_class(value: float) -> str:
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "neutral"


def summarize_tracker(df: pd.DataFrame, label: str, start_date, end_date=None) -> str:
    window = df[df["date"] >= start_date]
    if end_date is not None:
        window = window[window["date"] <= end_date]
    profit = float(window["profit_units"].sum()) if not window.empty else 0.0
    wins = int((window["result"] == "Win").sum()) if not window.empty else 0
    losses = int((window["result"] == "Loss").sum()) if not window.empty else 0
    pushes = int((window["result"] == "Push").sum()) if not window.empty else 0
    return (
        '<div class="glass metric-card">'
        f'<div class="metric-label">{safe(label)}</div>'
        f'<div class="metric-value {unit_class(profit)}">{format_units(profit)}</div>'
        f'<div class="subtle">{wins}W - {losses}L - {pushes}P</div>'
        "</div>"
    )


def render_tracker(now: datetime) -> None:
    st.subheader("Pick Tracker - Units P/L")
    history = load_pick_history()
    if not history:
        st.markdown('<div class="glass no-play"><strong>No settled picks yet</strong><br>Tracker will populate after picks are graded.</div>', unsafe_allow_html=True)
        return

    df = pd.DataFrame([pick.model_dump() for pick in history])
    df["date"] = pd.to_datetime(df["date"]).dt.date
    today = now.date()
    yesterday = today - timedelta(days=1)
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    all_start = df["date"].min()

    st.markdown(
        '<div class="tracker-grid">'
        + summarize_tracker(df, "All Time", all_start)
        + summarize_tracker(df, "This Year", year_start)
        + summarize_tracker(df, "This Month", month_start)
        + summarize_tracker(df, "This Week", week_start)
        + summarize_tracker(df, "Yesterday", yesterday, yesterday)
        + "</div>",
        unsafe_allow_html=True,
    )

    trend = df.sort_values("date").copy()
    trend["Cumulative Units"] = trend["profit_units"].cumsum()
    fig = px.line(
        trend,
        x="date",
        y="Cumulative Units",
        markers=True,
        hover_data=["selection", "league", "result", "profit_units"],
    )
    fig.update_traces(line=dict(color="#38f8ff", width=3), marker=dict(size=8, color="#a855f7"))
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=360, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    league_summary = (
        df.groupby(["sport", "league"], as_index=False)
        .agg(Picks=("selection", "count"), Units=("profit_units", "sum"), Wins=("result", lambda s: int((s == "Win").sum())), Losses=("result", lambda s: int((s == "Loss").sum())))
        .sort_values("Units", ascending=False)
    )
    display_df = df.sort_values("date", ascending=False).rename(
        columns={
            "date": "Date",
            "sport": "Sport",
            "league": "League",
            "selection": "Selection",
            "odds": "Odds",
            "stake_units": "Stake",
            "result": "Result",
            "profit_units": "Units",
        }
    )
    st.dataframe(league_summary, use_container_width=True, hide_index=True)
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def main() -> None:
    inject_css()
    scheduled_refresh()

    eastern = ZoneInfo("America/New_York")
    now = datetime.now(eastern)
    next_refresh = get_next_refresh_time(now)
    all_picks = load_top_picks()
    ranked = rank_picks(all_picks)
    export_df = export_board_rows(ranked)

    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">Prop Plug Pat</div>
            <h1>Elite Betting Board</h1>
            <div class="subtle">Disciplined, bankroll-focused rankings across MLB, WNBA, FIFA World Cup, and major sports.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_duel_simulator_launcher()

    action_cols = st.columns([1, 1, 1, 1])
    with action_cols[0]:
        if st.button("Refresh Board", use_container_width=True):
            st.rerun()
    with action_cols[1]:
        st.download_button(
            "Export CSV",
            data=export_df.to_csv(index=False),
            file_name=f"prop_plug_pat_board_{now:%Y%m%d_%H%M}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with action_cols[2]:
        card_metric("Last Updated", fmt_et(now), now.strftime("%b %d, %Y"))
    with action_cols[3]:
        card_metric("Next Auto Refresh", fmt_et(next_refresh), "9a, 12p, 2p, 6p, 7p")

    if len(ranked) < 10:
        st.warning("No weak picks were forced. The board is showing only plays that met the current mock confidence and edge threshold.")

    league_tabs = st.tabs(
        [
            "All Sports",
            "MLB",
            "WNBA",
            "FIFA World Cup",
            "WTA / Tennis",
            "Parlays",
            "Do Not Bet",
            "Simulations",
            "Tracker",
        ]
    )

    with league_tabs[0]:
        render_leaderboard("Top 10 Best Bets - All Sports", ranked)

    with league_tabs[1]:
        mlb_picks = [pick for pick in ranked if pick.league == "MLB"]
        render_leaderboard("MLB Betting Board", mlb_picks)
        render_hit_table("Best 3 MLB 1+ Hit Picks", load_hit_picks(), "hit_probability")
        render_hit_table("Best 5 MLB 1+ Hit/Run/RBI Picks", load_hrr_picks(), "probability")

    with league_tabs[2]:
        wnba_picks = [pick for pick in ranked if pick.league == "WNBA"]
        render_leaderboard("WNBA Betting Board", wnba_picks)

    with league_tabs[3]:
        world_cup_picks = [pick for pick in ranked if pick.league == "FIFA World Cup"]
        render_leaderboard("FIFA World Cup Betting Board", world_cup_picks)
        render_world_cup_cards()

    with league_tabs[4]:
        tennis_picks = [pick for pick in ranked if pick.league == "WTA"]
        render_leaderboard("WTA / Tennis Betting Board", tennis_picks)

    with league_tabs[5]:
        render_moneyline_parlay()

    with league_tabs[6]:
        render_avoid_bets()

    with league_tabs[7]:
        render_simulations()

    with league_tabs[8]:
        render_tracker(now)

    st.markdown(
        """
        <div class="glass" style="margin-top: 1.5rem;">
            <strong>Responsible gambling:</strong> This dashboard is for analysis and entertainment only.
            Betting involves risk, and no outcome is guaranteed. Keep stakes disciplined, never chase losses,
            and only wager what you can afford to lose.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
