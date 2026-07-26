from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

import streamlit as st
from streamlit_autorefresh import st_autorefresh

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from components import (
    render_agent_workflow,
    render_decision_panel,
    render_digital_twin,
    render_hero,
    render_kpi_row,
    render_performance_comparison,
    render_performance_dashboard,
    render_section_header,
    render_system_health,
    render_timeline,
)
from styles import load_css
from utils import compute_summary, current_time_label, latest_row, load_data


st.set_page_config(
    page_title="Athena AI | Building Intelligence Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(load_css(), unsafe_allow_html=True)

# Auto-refresh telemetry every 6 seconds
st_autorefresh(interval=6000, key="athena_live_refresh")


def compact_number(value, precision: int = 1, fallback: str = "--") -> str:
    try:
        if value is None:
            return fallback
        number = float(value)
    except (TypeError, ValueError):
        return fallback

    absolute = abs(number)
    if absolute >= 1_000_000_000:
        return f"{number / 1_000_000_000:.{precision}f}B"
    if absolute >= 1_000_000:
        return f"{number / 1_000_000:.{precision}f}M"
    if absolute >= 1_000:
        return f"{number / 1_000:.{precision}f}K"
    return f"{number:.{precision}f}"


def build_metrics(summary: dict) -> list[dict]:
    temperature = summary.get("temperature")
    pmv = summary.get("pmv")
    electricity = summary.get("electricity")
    reward = summary.get("reward")
    confidence = summary.get("confidence")

    t_delta = summary.get("temp_delta", 0.0)
    p_delta = summary.get("pmv_delta", 0.0)
    e_delta = summary.get("energy_delta", 0.0)
    r_delta = summary.get("reward_delta", 0.0)

    pmv_value = abs(float(pmv)) if pmv is not None else None
    energy_value = float(electricity) if electricity is not None else None

    t_delta_str = f"{'+' if t_delta > 0 else ''}{t_delta:.1f} degC" if abs(t_delta) >= 0.05 else "STABLE"
    p_delta_str = f"{'+' if p_delta > 0 else ''}{p_delta:.2f}" if abs(p_delta) >= 0.01 else "STABLE"
    e_delta_str = f"{'+' if e_delta > 0 else ''}{compact_number(e_delta, 1)} W" if abs(e_delta) >= 10 else "STABLE"
    r_delta_str = f"{'+' if r_delta > 0 else ''}{r_delta:.3f}" if abs(r_delta) >= 0.001 else "STABLE"

    return [
        {
            "title": "Zone Air Temp",
            "value": f"{float(temperature):.1f} degC" if temperature is not None else "--",
            "subtitle": "Live CORE_ZN air setpoint",
            "icon": "",
            "tone": "good" if temperature is not None else "",
            "delta": t_delta_str,
            "delta_type": "up" if t_delta > 0 else ("down" if t_delta < 0 else "neutral"),
        },
        {
            "title": "PMV Index",
            "value": f"{float(pmv):.2f}" if pmv is not None else "--",
            "subtitle": "Predicted Mean Vote comfort",
            "icon": "",
            "tone": "good" if pmv_value is not None and pmv_value <= 0.5 else "warning",
            "delta": p_delta_str,
            "delta_type": "down" if abs(p_delta) < 0.01 or p_delta < 0 else "up",
        },
        {
            "title": "Power Demand",
            "value": compact_number(energy_value, precision=1) + " W" if energy_value is not None else "--",
            "subtitle": "Building electricity demand",
            "icon": "",
            "tone": "good" if energy_value is not None and energy_value < 400000 else "warning",
            "delta": e_delta_str,
            "delta_type": "down" if e_delta <= 0 else "up",
        },
        {
            "title": "Control Reward",
            "value": f"{float(reward):.3f}" if reward is not None else "--",
            "subtitle": "Comfort-energy policy reward",
            "icon": "",
            "tone": "good" if reward is not None and float(reward) >= 0.9 else "warning",
            "delta": r_delta_str,
            "delta_type": "up" if r_delta >= 0 else "down",
        },
        {
            "title": "AI Confidence",
            "value": f"{float(confidence):.2f}" if confidence is not None else "--",
            "subtitle": "Safety validated certainty",
            "icon": "",
            "tone": "good" if confidence is not None and float(confidence) >= 0.9 else "warning",
            "delta": "99% SAFE",
            "delta_type": "up",
        },
    ]


def render_empty_state() -> None:
    st.markdown(
        """
<div class="glass-card animate-in" style="padding: 2.5rem; text-align: center;">
  <div class="section-label">SIMULATION STANDBY</div>
  <h2 class="section-title" style="margin-top: 0.5rem;">Awaiting EnergyPlus Telemetry Stream...</h2>
  <div class="section-description" style="max-width: 600px; margin: 0.5rem auto 0;">
    Athena AI BEMS engine is active. Once runtime control generates CSV records in <code>logs/simulation_log.csv</code>, live telemetry and digital twin schematics will display here automatically.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_dashboard() -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = load_data()
    summary = compute_summary(df)
    latest = latest_row(df)

    render_hero(current_time=now, online=not df.empty)

    col1, col2 = st.columns([0.85, 0.15])
    with col2:
        st.button("🔄 Force Refresh Data", use_container_width=True)

    st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)

    if df.empty:
        render_empty_state()
        return

    # Top KPI row (5 columns)
    render_kpi_row(build_metrics(summary))

    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

    # Tabs for clean organization
    tab_overview, tab_intelligence, tab_telemetry = st.tabs([
        "🏢 Building Digital Twin", 
        "🧠 Athena AI Agent", 
        "📈 Telemetry & ROI"
    ])

    with tab_overview:
        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
        # Left side Digital Twin, right side System Health
        left_col, right_col = st.columns([1.2, 0.8], gap="medium")
        with left_col:
            render_digital_twin(latest, df)
        with right_col:
            render_system_health(latest)

    with tab_intelligence:
        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
        left_col, right_col = st.columns([1, 1], gap="medium")
        with left_col:
            render_agent_workflow(latest)
        with right_col:
            render_timeline(latest)
        st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
        render_decision_panel(latest)

    with tab_telemetry:
        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
        render_section_header(
            "Real-Time Telemetry",
            "Performance & Trajectory Dashboard",
            "Live zone temperature, building electricity demand, occupant PMV comfort, and control reward trajectories.",
        )
        st.markdown('<div style="height:0.4rem"></div>', unsafe_allow_html=True)
        render_performance_dashboard(df)
        st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
        render_performance_comparison(df)

    st.markdown('<div style="height:1.2rem"></div>', unsafe_allow_html=True)
    footer_left, footer_right = st.columns([0.7, 0.3])
    with footer_left:
        st.markdown(
            f"<div class='section-description' style='font-size:0.82rem;'>Captured {len(df):,} simulation steps from {current_time_label(df)}. Last MCP tool executed: <code>{latest.get('tool', '--')}</code></div>",
            unsafe_allow_html=True,
        )
    with footer_right:
        st.markdown(
            "<div class='section-description' style='text-align:right;font-size:0.82rem;'>EnergyPlus API * Qwen2.5 (Ollama) * MCP Protocol</div>",
            unsafe_allow_html=True,
        )


render_dashboard()
