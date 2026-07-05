from __future__ import annotations

import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from services.mock_data import (
    load_avoid_bets,
    load_hit_picks,
    load_hrr_picks,
    load_moneyline_parlay,
    load_pick_history,
    load_top_picks,
)
from utils import rank_picks


st.set_page_config(
    page_title="Prop Plug Pat - Betting AI Assistant",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            color: #f6f1ff;
            background:
                radial-gradient(circle at 18% 0%, rgba(124, 58, 237, 0.26), transparent 34%),
                radial-gradient(circle at 86% 12%, rgba(56, 248, 255, 0.13), transparent 32%),
                linear-gradient(180deg, #050508 0%, #090711 55%, #050508 100%);
        }
        [data-testid="stHeader"] { background: transparent; }
        .hero {
            padding: 1.2rem 0 0.8rem;
            border-bottom: 1px solid rgba(168, 85, 247, 0.22);
            margin-bottom: 1rem;
        }
        .eyebrow {
            color: #38f8ff;
            font-size: 0.78rem;
            letter-spacing: 0.18rem;
            text-transform: uppercase;
            font-weight: 800;
        }
        h1 {
            font-size: clamp(2rem, 5vw, 4rem);
            line-height: 0.95;
            color: #fff;
            text-shadow: 0 0 32px rgba(168, 85, 247, 0.5);
        }
        .glass {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.09), rgba(255, 255, 255, 0.035));
            border: 1px solid rgba(177, 108, 255, 0.24);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(14px);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.8rem;
        }
        .subtle { color: #b8acc8; }
        .badge {
            display: inline-flex;
            border-radius: 999px;
            padding: 0.22rem 0.58rem;
            font-size: 0.76rem;
            font-weight: 900;
            margin: 0.15rem 0.25rem 0.15rem 0;
            border: 1px solid rgba(255,255,255,0.14);
            background: rgba(168, 85, 247, 0.18);
        }
        .stButton > button, .stLinkButton > a {
            background: linear-gradient(135deg, #7c3aed, #a855f7);
            color: white;
            border: 1px solid rgba(255,255,255,0.16);
            border-radius: 8px;
            font-weight: 800;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def fmt_odds(odds: int) -> str:
    return f"+{odds}" if odds > 0 else str(odds)


def fmt_units(value: float) -> str:
    prefix = "+" if value > 0 else ""
    return f"{prefix}{value:.2f}u"


def get_context() -> dict:
    ranked = rank_picks(load_top_picks())
    history = pd.DataFrame([pick.model_dump() for pick in load_pick_history()])
    if not history.empty:
        history["date"] = pd.to_datetime(history["date"]).dt.date
    return {
        "ranked": ranked,
        "avoid": load_avoid_bets(),
        "hit_picks": load_hit_picks(),
        "hrr_picks": load_hrr_picks(),
        "parlay": load_moneyline_parlay(),
        "history": history,
    }


def pick_lines(picks, limit: int = 5) -> str:
    lines = []
    for index, pick in enumerate(picks[:limit], start=1):
        lines.append(
            f"{index}. {pick.selection} ({pick.league}, {pick.start_time_et}) - "
            f"{pick.grade.value}, {pick.confidence:.1f}/10, {pick.probability:.1f}% probability, "
            f"{pick.edge:.1f}% edge, stake {pick.recommended_stake}. Matchup: {pick.matchup}."
        )
    return "\n".join(lines)


def avoid_lines(avoid, limit: int = 6) -> str:
    return "\n".join(
        f"{i}. Avoid {item.bet} ({item.matchup}, {item.start_time_et}, {fmt_odds(item.sportsbook_odds)}): {item.reason}"
        for i, item in enumerate(avoid[:limit], start=1)
    )


def tracker_summary(history: pd.DataFrame) -> str:
    if history.empty:
        return "No settled pick history is loaded yet."
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
            "Bankroll mode: use 1 unit as 1% of bankroll for normal edges, 0.25u-0.5u for leans, "
            "and 1.25u max for the strongest A+ edges. Tell me your bankroll amount and I can convert units to dollars."
        )
    unit = bankroll * 0.01
    return (
        f"With a ${bankroll:,.0f} bankroll, 1u = ${unit:,.2f}.\n"
        f"A+ max stake around 1.25u = ${unit * 1.25:,.2f}; normal A stake 1u = ${unit:,.2f}; "
        f"B+ lean 0.5u = ${unit * 0.5:,.2f}. Keep the daily exposure capped before adding parlays."
    )


def answer_user(message: str, context: dict) -> str:
    text = message.lower()
    ranked = context["ranked"]

    if any(word in text for word in ["avoid", "trap", "do not", "don't bet", "dont bet"]):
        return "Specific plays to avoid right now:\n\n" + avoid_lines(context["avoid"])

    if any(word in text for word in ["tracker", "profit", "loss", "p/l", "units", "record"]):
        return "Current tracked unit performance:\n\n" + tracker_summary(context["history"])

    if "parlay" in text:
        parlay = context["parlay"]
        legs = "\n".join(
            f"- {leg.leg} ({leg.league}, {leg.start_time_et}) at {fmt_odds(leg.estimated_odds)}: {leg.reason}"
            for leg in parlay.legs
        )
        removes = ", ".join(parlay.safer_removes) or "No removal suggested."
        return (
            f"Best strict moneyline parlay: {fmt_odds(parlay.estimated_odds)}, "
            f"{parlay.combined_probability:.1f}% combined probability, risk {parlay.risk_rating}.\n\n"
            f"{legs}\n\nSafer-card remove: {removes}"
        )

    if "mlb" in text and ("hit" in text or "hrr" in text or "rbi" in text or "run" in text):
        hits = "\n".join(
            f"- {p.player} 1+ hit ({p.team} vs {p.opponent}, {p.start_time_et}): {p.hit_probability:.1f}%, {p.grade.value}. {p.reasoning}"
            for p in context["hit_picks"]
        )
        hrr = "\n".join(
            f"- {p.player} hit/run/RBI ({p.team} vs {p.opponent}, {p.start_time_et}): {p.probability:.1f}%, {p.grade.value}. {p.reasoning}"
            for p in context["hrr_picks"]
        )
        return f"Best MLB hit props:\n{hits}\n\nBest MLB hit/run/RBI props:\n{hrr}"

    if any(word in text for word in ["bankroll", "stake", "unit", "wager", "$"]):
        return bankroll_answer(message)

    if "wnba" in text:
        picks = [pick for pick in ranked if pick.league == "WNBA"]
        return "WNBA board:\n\n" + (pick_lines(picks) if picks else "No WNBA play meets the current threshold.")

    if "world cup" in text or "fifa" in text or "soccer" in text:
        picks = [pick for pick in ranked if pick.league == "FIFA World Cup"]
        return "FIFA World Cup board:\n\n" + (pick_lines(picks) if picks else "No World Cup play meets the current threshold.")

    if "tennis" in text or "wta" in text:
        picks = [pick for pick in ranked if pick.league == "WTA"]
        return "WTA/Tennis board:\n\n" + (pick_lines(picks) if picks else "No tennis play meets the current threshold.")

    if "best" in text or "top" in text or "today" in text or "pick" in text:
        return "Top ranked plays right now:\n\n" + pick_lines(ranked, limit=10)

    return (
        "I can help with best bets, sport-specific cards, MLB hit props, parlays, do-not-bet traps, "
        "bankroll sizing, and unit tracking. Try asking: 'What are the top 5 plays?', "
        "'What should I avoid?', 'Build the safest parlay', or 'My bankroll is $500, what should I stake?'"
    )


def main() -> None:
    inject_css()
    context = get_context()

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">Prop Plug Pat</div>
            <h1>Sports Betting AI Chatbot</h1>
            <div class="subtle">Ask for best bets, avoids, parlays, staking, MLB props, or unit tracking. Uses the current board data without paid API calls.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Back to Elite Betting Board", use_container_width=True):
        st.switch_page("app.py")

    quick_cols = st.columns(4)
    quick_prompts = [
        "What are the top 5 plays?",
        "What specific plays should I avoid?",
        "Build the safest parlay.",
        "Show tracker profit/loss.",
    ]
    for col, prompt in zip(quick_cols, quick_prompts):
        with col:
            if st.button(prompt, use_container_width=True):
                st.session_state.chat_prompt = prompt

    if "bet_chat_messages" not in st.session_state:
        st.session_state.bet_chat_messages = [
            {
                "role": "assistant",
                "content": "Welcome to the betting desk. I will stay disciplined: no forced plays, no guarantees, and bankroll first.",
            }
        ]

    for message in st.session_state.bet_chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.session_state.pop("chat_prompt", None) or st.chat_input("Ask the betting assistant...")
    if prompt:
        st.session_state.bet_chat_messages.append({"role": "user", "content": prompt})
        response = answer_user(prompt, context)
        st.session_state.bet_chat_messages.append({"role": "assistant", "content": response})
        st.rerun()

    st.markdown(
        """
        <div class="glass">
            <strong>Responsible gambling:</strong> This assistant is for analysis and entertainment only.
            It does not guarantee outcomes. Keep stakes disciplined and never chase losses.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
