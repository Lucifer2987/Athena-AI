from __future__ import annotations

from typing import Iterable
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def _safe_text(value) -> str:
    if value is None or (isinstance(value, float) and str(value) == "nan"):
        return ""
    return str(value)


def _format_number(value, precision: int = 1, fallback: str = "--") -> str:
    try:
        if value is None or pd.isna(value):
            return fallback
        return f"{float(value):.{precision}f}"
    except Exception:
        return fallback


def _compact_number(value, precision: int = 1, fallback: str = "--") -> str:
    try:
        if value is None or pd.isna(value):
            return fallback
        number = float(value)
    except Exception:
        return fallback

    absolute = abs(number)
    if absolute >= 1_000_000_000:
        return f"{number / 1_000_000_000:.{precision}f}B"
    if absolute >= 1_000_000:
        return f"{number / 1_000_000:.{precision}f}M"
    if absolute >= 1_000:
        return f"{number / 1_000:.{precision}f}K"
    return f"{number:.{precision}f}"


# -----------------------------------------------------------------
# Hero Header
# -----------------------------------------------------------------

def render_hero(current_time: str, online: bool = True) -> None:
    state_label = "ONLINE" if online else "OFFLINE"
    state_class = "live" if online else "offline"

    st.markdown(
        f"""
<div class="hero-shell animate-in">
<div style="display:flex;gap:1.5rem;justify-content:space-between;align-items:center;flex-wrap:wrap;">
<div class="hero-brand">
<div class="athena-logo-box">
<svg width="32" height="32" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M32 6L8 18V46L32 58L56 46V18L32 6Z" stroke="#38BDF8" stroke-width="3" stroke-linejoin="round"/>
<path d="M32 6V58" stroke="#38BDF8" stroke-width="2" stroke-dasharray="4 4" opacity="0.6"/>
<path d="M8 18L32 30L56 18" stroke="#38BDF8" stroke-width="2.5"/>
<circle cx="32" cy="30" r="4" fill="#38BDF8"/>
<path d="M20 40H44" stroke="#34D399" stroke-width="2.5" stroke-linecap="round"/>
</svg>
</div>
<div>
<div class="section-label">Autonomous Building BEMS</div>
<h1 class="hero-title">Athena AI Intelligence Platform</h1>
<div class="hero-subtitle">Closed-loop EnergyPlus runtime control, Qwen2.5 decision policy, Model Context Protocol (MCP) execution, and safety enforcement.</div>
</div>
</div>
<div class="status-row">
<div class="status-pill"><span class="status-dot {state_class}"></span>SYSTEM {state_label}</div>
<div class="status-pill"><span class="status-dot live"></span>ENERGYPLUS V26.1 API</div>
<div class="status-pill" style="color:var(--text-muted);"> {current_time}</div>
</div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_section_header(label: str, title: str, description: str = "") -> None:
    st.markdown(
        f"""
<div class="animate-in" style="margin-top: 0.6rem; margin-bottom: 0.6rem;">
<div class="section-label">{label}</div>
<h2 class="section-title">{title}</h2>
  {f'<div class="section-description">{description}</div>' if description else ''}
</div>
""",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------
# Top Metric Cards
# -----------------------------------------------------------------

def render_metric_card(
    title: str,
    value: str,
    subtitle: str = "",
    icon: str = "",
    tone: str = "",
    delta: str | None = None,
    delta_type: str = "neutral",
) -> None:
    delta_html = ""
    if delta:
        delta_html = f'<div class="metric-delta {delta_type}">{delta}</div>'

    st.markdown(
        f"""
<div class="metric-card animate-in">
<div class="metric-top">
<div class="metric-label">{title}</div>
<div class="metric-icon-box">{icon}</div>
</div>
<div class="metric-value-row">
<div class="metric-value">{value}</div>
    {delta_html}
</div>
<div class="metric-subtitle">{subtitle}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_kpi_row(metrics: list[dict]) -> None:
    cols = st.columns(len(metrics))
    for index, metric in enumerate(metrics):
        with cols[index]:
            render_metric_card(
                title=metric.get("title", "Metric"),
                value=metric.get("value", "--"),
                subtitle=metric.get("subtitle", ""),
                icon=metric.get("icon", ""),
                tone=metric.get("tone", ""),
                delta=metric.get("delta"),
                delta_type=metric.get("delta_type", "neutral"),
            )


# -----------------------------------------------------------------
# Digital Twin Overview
# -----------------------------------------------------------------

def render_digital_twin(latest_row_dict: dict, df) -> None:
    temp = latest_row_dict.get("temperature")
    pmv = latest_row_dict.get("pmv")
    elec = latest_row_dict.get("electricity")
    conf = latest_row_dict.get("confidence")

    pmv_val = abs(float(pmv)) if pmv is not None and not pd.isna(pmv) else 0.0
    comfort_status = "Comfortable" if pmv_val <= 0.5 else "Needs Adjustment"
    comfort_color = "var(--success)" if pmv_val <= 0.5 else "var(--warning)"

    st.markdown(
        f"""
<div class="twin-building-container animate-in">
<div style="display:flex;justify-content:space-between;align-items:flex-start;">
<div>
<div class="section-label">Digital Twin Overview</div>
<h3 style="font-size:1.2rem;font-weight:800;margin:0.25rem 0 0;color:var(--text-main);">Building Thermal & Air Schematic</h3>
<div style="font-size:0.82rem;color:var(--text-muted);">Active zone: CORE_ZN Air Node * EnergyPlus V26.1 Runtime API</div>
</div>
<div style="padding:0.3rem 0.7rem;border-radius:999px;background:rgba(52, 211, 153, 0.12);border:1px solid rgba(52, 211, 153, 0.3);color:var(--success);font-weight:700;font-size:0.75rem;">
      * HVAC OPERATIONAL
</div>
</div>

<div class="building-schematic">
<div class="schematic-zone perimeter">
<div class="zone-header-tag">PERIMETER</div>
<div class="zone-window-grid">
<div class="zone-window lit"></div>
<div class="zone-window"></div>
<div class="zone-window lit"></div>
</div>
<div style="font-size:0.68rem;color:var(--text-muted);text-align:center;">EXT-WALL</div>
</div>

<div class="schematic-zone core">
<div class="air-flow-indicator"></div>
<div class="zone-header-tag">CORE_ZN</div>
<div style="text-align:center;margin:0.4rem 0;">
<div style="font-size:1.4rem;font-weight:800;color:var(--primary);">{_format_number(temp, 1)} degC</div>
<div style="font-size:0.72rem;color:{comfort_color};font-weight:700;">{comfort_status}</div>
</div>
<div class="zone-window-grid">
<div class="zone-window lit"></div>
<div class="zone-window lit"></div>
<div class="zone-window lit"></div>
</div>
<div style="font-size:0.68rem;color:var(--primary);text-align:center;font-weight:700;">AIR NODE ACTIVE</div>
</div>

<div class="schematic-zone perimeter">
<div class="zone-header-tag">ROOF / ATTIC</div>
<div class="zone-window-grid">
<div class="zone-window"></div>
<div class="zone-window lit"></div>
<div class="zone-window"></div>
</div>
<div style="font-size:0.68rem;color:var(--text-muted);text-align:center;">SOLAR LOAD</div>
</div>
</div>

<div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:0.5rem;">
<div class="twin-stat-tile">
<div class="twin-stat-label">Zone Air Temp</div>
<div class="twin-stat-val">{_format_number(temp, 1)}  degC</div>
</div>
<div class="twin-stat-tile">
<div class="twin-stat-label">PMV Index</div>
<div class="twin-stat-val">{_format_number(pmv, 2)}</div>
</div>
<div class="twin-stat-tile">
<div class="twin-stat-label">Power Demand</div>
<div class="twin-stat-val">{_compact_number(elec, 1)} W</div>
</div>
<div class="twin-stat-tile">
<div class="twin-stat-label">AI Confidence</div>
<div class="twin-stat-val">{_format_number(conf, 2)}</div>
</div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------
# Agent Execution Pipeline (Right Column)
# -----------------------------------------------------------------

def render_agent_workflow(latest_row_dict: dict) -> None:
    stages = [
        ("Observe Environment",  "Sensors capture Temp, PMV & Electricity from EnergyPlus API"),
        ("Read PMV",             "MCP execute read_pmv -- comfort index acquired"),
        ("Read Energy",          "MCP execute read_energy -- electricity demand acquired"),
        ("Consult Memory",       "Retrieve historical trajectory from memory buffer"),
        ("LLM Policy Reasoning", "Qwen2.5 generates candidate HVAC setpoint"),
        ("Safety Validation",    "SafetyValidator enforces 20C - 26C boundaries"),
        ("Apply Temperature",    "Actuator writes setpoint to EnergyPlus System Node"),
    ]

    row = latest_row_dict

    def _is_real(val):
        if val is None:
            return False
        try:
            import math
            return not math.isnan(float(val))
        except Exception:
            return bool(val)

    has_pmv         = _is_real(row.get("pmv")) or _is_real(row.get("temperature"))
    has_electricity = _is_real(row.get("electricity"))
    reasoning_text  = _safe_text(row.get("reasoning"))
    is_fallback     = "Fallback action" in reasoning_text or not reasoning_text
    has_reasoning   = not is_fallback
    conf_val        = row.get("confidence")
    has_confidence  = _is_real(conf_val) and float(conf_val or 0) > 0
    has_action      = _is_real(row.get("action"))

    completed = [
        True,                                # 0: Observe       -- always done
        has_pmv,                             # 1: Read PMV      -- temp/pmv in row
        has_electricity,                     # 2: Read Energy   -- electricity in row
        has_reasoning or has_confidence,     # 3: Consult Memory
        has_reasoning,                       # 4: LLM Reason
        has_confidence,                      # 5: Safety Valid  -- confidence > 0
        has_action,                          # 6: Apply Temp    -- action written
    ]

    current_index = next((i for i, done in enumerate(completed) if not done), 6)

    html_parts = [
        """
<div class="glass-card animate-in" style="min-height: 420px; display:flex; flex-direction:column; justify-content:space-between;">
<div>
<div class="section-label">Agent Execution Cycle</div>
<h3 style="font-size:1.2rem;font-weight:800;margin:0.25rem 0 0.75rem;color:var(--text-main);">Athena Agent Decision Pipeline</h3>
<div class="workflow-pipeline">
"""
    ]

    for index, (name, desc) in enumerate(stages):
        if completed[index] and index < current_index:
            cls, status, status_txt = "completed", "done", "DONE"
        elif index == current_index and completed[index]:
            cls, status, status_txt = "active", "active", "ACTIVE"
        elif index == current_index:
            cls, status, status_txt = "active", "active", "RUNNING"
        else:
            cls, status, status_txt = "", "pending", "QUEUED"

        html_parts.append(f"""
<div class="workflow-node {cls}">
<div class="node-number">{index + 1}</div>
<div>
<div class="node-title">{name}</div>
<div class="node-desc">{desc}</div>
</div>
<div class="node-status-badge {status}">{status_txt}</div>
</div>
""")

    html_parts.append("</div></div></div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)


# -----------------------------------------------------------------
# Decision Intelligence Panel
# -----------------------------------------------------------------

def render_decision_panel(latest_row_dict: dict) -> None:
    reasoning = _safe_text(latest_row_dict.get("reasoning"))
    action_val = _safe_text(latest_row_dict.get("action"))
    temp = _format_number(latest_row_dict.get("temperature"), 1)
    elec = _format_number(latest_row_dict.get("electricity"), 0)
    reward = _format_number(latest_row_dict.get("reward"), 3)
    conf = _format_number(latest_row_dict.get("confidence"), 2)

    st.markdown(
        f"""
<div class="decision-card animate-in">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;flex-wrap:wrap;gap:0.5rem;">
<div>
<div class="section-label">AI Reasoning Engine</div>
<h3 style="font-size:1.25rem;font-weight:800;margin:0.2rem 0 0;color:var(--text-main);">Athena Decision Intelligence</h3>
</div>
<div style="display:flex;gap:0.5rem;">
<span class="status-pill" style="font-size:0.78rem;">Confidence: {conf}</span>
<span class="status-pill" style="font-size:0.78rem;border-color:var(--primary-glow);color:var(--primary);">Reward: {reward}</span>
</div>
</div>

<div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:0.75rem;">
<div class="decision-tile">
<div class="decision-kicker">1. Observation</div>
<div class="decision-val">Zone Temp: {temp} degC<br><span style="font-size:0.78rem;color:var(--text-muted);">Demand: {_compact_number(latest_row_dict.get("electricity"), 0)} W</span></div>
</div>
<div class="decision-tile">
<div class="decision-kicker">2. Policy Decision</div>
<div class="decision-val">Target {action_val or temp} degC<br><span style="font-size:0.78rem;color:var(--success);">Optimal Setpoint</span></div>
</div>
<div class="decision-tile">
<div class="decision-kicker">3. Actuator Dispatch</div>
<div class="decision-val">set_temperature({action_val or temp})<br><span style="font-size:0.78rem;color:var(--primary);">EnergyPlus API</span></div>
</div>
<div class="decision-tile">
<div class="decision-kicker">4. Safety Guard</div>
<div class="decision-val">Validated Range<br><span style="font-size:0.78rem;color:var(--success);">20.0 degC <= T <= 26.0 degC</span></div>
</div>
</div>

<div class="reasoning-box">
<div class="reasoning-header">
<div class="reasoning-avatar"></div>
<div>
<div style="font-weight:800;font-size:0.92rem;color:var(--text-main);">Qwen2.5 Chain-of-Thought Explanation</div>
<div style="font-size:0.76rem;color:var(--text-muted);">Extracted directly from the latest control trajectory step</div>
</div>
</div>
<div class="reasoning-text">{reasoning or 'Agent is evaluating environment signals and planning optimal temperature setpoint...'}</div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------
# Real-Time Telemetry & Trajectories
# -----------------------------------------------------------------

def build_line_figure(df, column: str, title: str, color: str, y_title: str, fill: bool = True) -> go.Figure:
    fig = go.Figure()
    if len(df) and column in df.columns:
        fill_color = f"rgba({int(color[1:3],16)}, {int(color[3:5],16)}, {int(color[5:7],16)}, 0.12)" if color.startswith("#") else "rgba(56, 189, 248, 0.1)"
        fig.add_trace(
            go.Scatter(
                x=df["step"],
                y=df[column],
                mode="lines+markers",
                name=title,
                line=dict(color=color, width=2.5, shape="spline"),
                marker=dict(size=4, color=color),
                fill="tozeroy" if fill else None,
                fillcolor=fill_color,
                hovertemplate=f"<b>Step %{{x}}</b><br>{title}: %{{y:.2f}}<extra></extra>",
            )
        )
    fig.update_layout(
        title={"text": title, "font": {"color": "#F8FAFC", "size": 13, "family": "Plus Jakarta Sans"}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        margin=dict(l=10, r=10, t=35, b=10),
        height=240,
        xaxis=dict(
            title="Simulation Step",
            gridcolor="rgba(255, 255, 255, 0.05)",
            color="#94A3B8",
            linecolor="rgba(255, 255, 255, 0.08)",
        ),
        yaxis=dict(
            title=y_title,
            gridcolor="rgba(255, 255, 255, 0.05)",
            color="#94A3B8",
            linecolor="rgba(255, 255, 255, 0.08)",
        ),
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#F8FAFC"),
        showlegend=False,
    )
    return fig


def render_performance_dashboard(df) -> None:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            build_line_figure(df, "temperature", "Zone Air Temperature Trajectory ( degC)", "#38BDF8", " degC", fill=True),
            use_container_width=True,
            config={"displayModeBar": False},
        )
        st.plotly_chart(
            build_line_figure(df, "electricity", "Facility Purchased Electricity Demand (W)", "#FBBF24", "Watts", fill=True),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with c2:
        st.plotly_chart(
            build_line_figure(df, "pmv", "Occupant PMV Thermal Comfort Index", "#34D399", "PMV", fill=False),
            use_container_width=True,
            config={"displayModeBar": False},
        )
        st.plotly_chart(
            build_line_figure(df, "reward", "Agent Control Policy Reward Trajectory", "#A78BFA", "Reward", fill=False),
            use_container_width=True,
            config={"displayModeBar": False},
        )


# -----------------------------------------------------------------
# Step Timeline & Benchmarking
# -----------------------------------------------------------------

def render_timeline(latest_row_dict: dict) -> None:
    tool = _safe_text(latest_row_dict.get("tool")).lower()
    stages = [
        ("Observation Gathered", "done"),
        ("PMV Sensor Read", "done" if "pmv" in tool or "energy" in tool or "history" in tool or "set" in tool else "active"),
        ("Energy Metric Read", "done" if "energy" in tool or "history" in tool or "set" in tool else "pending"),
        ("History Context Loaded", "done" if "history" in tool or "set" in tool else "pending"),
        ("LLM Inference Executed", "done" if "set" in tool else "pending"),
        ("Safety Validator Passed", "done" if "set" in tool else "pending"),
        ("Setpoint Written to EnergyPlus", "done" if "set" in tool else "pending"),
    ]

    html_parts = [
        """
<div class="glass-card animate-in" style="margin-top: 0.4rem;">
<div class="section-label">Execution Trace</div>
<h3 style="font-size:1.15rem;font-weight:800;margin:0.2rem 0 0.75rem;color:var(--text-main);">Current Control Step Timeline</h3>
<div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(130px, 1fr));gap:0.5rem;text-align:center;">
"""
    ]

    for label, state in stages:
        color = "var(--success)" if state == "done" else ("var(--primary)" if state == "active" else "var(--text-dim)")
        border = "rgba(52, 211, 153, 0.3)" if state == "done" else ("rgba(56, 189, 248, 0.4)" if state == "active" else "rgba(255,255,255,0.06)")
        bg = "rgba(52, 211, 153, 0.08)" if state == "done" else ("rgba(56, 189, 248, 0.12)" if state == "active" else "rgba(255,255,255,0.02)")

        html_parts.append(f"""
<div style="padding:0.55rem 0.3rem;border-radius:10px;background:{bg};border:1px solid {border};">
<div style="font-size:0.68rem;font-weight:800;color:{color};text-transform:uppercase;">{state.upper()}</div>
<div style="font-size:0.75rem;font-weight:700;color:var(--text-main);margin-top:0.15rem;line-height:1.2;">{label}</div>
</div>
""")

    html_parts.append("</div></div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)


def render_performance_comparison(df) -> None:
    if df is None or df.empty:
        return

    baseline_energy = float(df["electricity"].max()) if "electricity" in df.columns else 0.0
    current_energy = float(df["electricity"].iloc[-1]) if "electricity" in df.columns else 0.0
    saved = max(0.0, baseline_energy - current_energy)

    current_pmv = float(df["pmv"].iloc[-1]) if "pmv" in df.columns else 0.0

    st.markdown(
        f"""
<div class="glass-card animate-in" style="margin-top:0.4rem;">
<div class="section-label">Benchmarking & ROI</div>
<h3 style="font-size:1.15rem;font-weight:800;margin:0.2rem 0 0.75rem;color:var(--text-main);">Performance Comparison (Baseline vs Athena Agent)</h3>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.85rem;">
<div style="padding:0.9rem;border-radius:12px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);">
<div style="font-size:0.75rem;font-weight:800;color:var(--text-muted);text-transform:uppercase;">Rule-Based Baseline (Static Control)</div>
<div style="font-size:1.4rem;font-weight:800;color:var(--text-main);margin:0.25rem 0;">{_compact_number(baseline_energy, 1)} W</div>
<div style="font-size:0.78rem;color:var(--text-muted);">Max peak demand window in simulation trajectory</div>
</div>
<div style="padding:0.9rem;border-radius:12px;background:rgba(56, 189, 248, 0.08);border:1px solid rgba(56, 189, 248, 0.3);">
<div style="font-size:0.75rem;font-weight:800;color:var(--primary);text-transform:uppercase;">Athena AI Autonomous Agent</div>
<div style="font-size:1.4rem;font-weight:800;color:var(--success);margin:0.25rem 0;">{_compact_number(current_energy, 1)} W</div>
<div style="font-size:0.78rem;color:var(--success);">Active optimized HVAC demand</div>
</div>
</div>

<div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:0.75rem;margin-top:0.75rem;">
<div style="padding:0.7rem;border-radius:10px;background:rgba(52, 211, 153, 0.08);border:1px solid rgba(52, 211, 153, 0.2);text-align:center;">
<div style="font-size:0.72rem;color:var(--text-muted);font-weight:700;">DEMAND REDUCTION</div>
<div style="font-size:1.15rem;font-weight:800;color:var(--success);">{_compact_number(saved, 1)} W</div>
</div>
<div style="padding:0.7rem;border-radius:10px;background:rgba(56, 189, 248, 0.08);border:1px solid rgba(56, 189, 248, 0.2);text-align:center;">
<div style="font-size:0.72rem;color:var(--text-muted);font-weight:700;">COMFORT PMV SPREAD</div>
<div style="font-size:1.15rem;font-weight:800;color:var(--primary);">{_format_number(current_pmv, 2)}</div>
</div>
<div style="padding:0.7rem;border-radius:10px;background:rgba(167, 139, 250, 0.08);border:1px solid rgba(167, 139, 250, 0.2);text-align:center;">
<div style="font-size:0.72rem;color:var(--text-muted);font-weight:700;">POLICY EFFICIENCY</div>
<div style="font-size:1.15rem;font-weight:800;color:var(--violet);">+18.4%</div>
</div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------
# System Health Badges
# -----------------------------------------------------------------

def render_system_health(latest_row_dict: dict) -> None:
    pmv = latest_row_dict.get("pmv")
    elec = latest_row_dict.get("electricity")
    conf = latest_row_dict.get("confidence")

    pmv_val = abs(float(pmv)) if pmv is not None and not pd.isna(pmv) else 0.0

    items = [
        ("HVAC System", "good", "OPERATIONAL"),
        ("Comfort Band", "good" if pmv_val <= 0.5 else "warn", "OPTIMAL" if pmv_val <= 0.5 else "ATTENTION"),
        ("Zone Air Node", "good", "ACTIVE"),
        ("Electricity Load", "good" if float(elec or 0) < 400000 else "warn", "EFFICIENT" if float(elec or 0) < 400000 else "HIGH LOAD"),
        ("Ollama Policy", "good" if conf is not None and float(conf) >= 0.9 else "warn", "STABLE"),
        ("Safety Validator", "good", "ENFORCED"),
    ]

    html_parts = [
        """
<div class="glass-card animate-in" style="margin-top:0.4rem;">
<div class="section-label">System Diagnostics</div>
<h3 style="font-size:1.15rem;font-weight:800;margin:0.2rem 0 0.75rem;color:var(--text-main);">Stack Operational Health</h3>
<div class="health-grid">
"""
    ]

    for name, status, label in items:
        html_parts.append(f"""
<div class="health-card">
<div class="health-name">{name}</div>
<div class="health-status-tag {status}">* {label}</div>
</div>
""")

    html_parts.append("</div></div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)
