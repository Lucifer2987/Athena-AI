"""
Athena AI -- Quantitative Savings Report
Run: streamlit run dashboard/savings_report.py --server.port 8502

Proves % reductions in kWh consumed by Athena AI vs a rule-based baseline,
while maintaining thermal comfort (PMV in [-0.5, 0.5]).

Baseline = archived simulation_log_*.csv files (previous runs with default
           22-deg-C rule-based fallback control).
Athena   = current simulation_log.csv (optimised AI control, no fallbacks).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR    = CURRENT_DIR.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from styles import load_css

st.set_page_config(
    page_title="Athena AI | Savings Report",
    page_icon="chart_increasing",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(load_css(), unsafe_allow_html=True)

LOGS_DIR    = ROOT_DIR / "logs"
CURRENT_LOG = LOGS_DIR / "simulation_log.csv"


# -----------------------------------------------------------------
# Data loading helpers
# -----------------------------------------------------------------

def _read_csv(path: Path) -> pd.DataFrame:
    """Read a CSV with multi-encoding fallback."""
    for enc in ("utf-8", "utf-8-sig", "latin1"):
        try:
            df = pd.read_csv(path, encoding=enc)
            for col in ["temperature", "pmv", "electricity",
                        "reward", "action", "confidence", "step"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            return df.dropna(subset=["step"]).reset_index(drop=True)
        except Exception:
            continue
    return pd.DataFrame()


def load_current() -> pd.DataFrame:
    """Load the current (Athena-optimised) simulation log."""
    if not CURRENT_LOG.exists():
        return pd.DataFrame()
    return _read_csv(CURRENT_LOG)


def load_archived() -> pd.DataFrame:
    """Load all archived simulation logs as the baseline dataset.

    Archived files are named simulation_log_YYYYMMDD_HHMMSS.csv and were
    written during earlier runs that used rule-based / fallback control.
    """
    frames = []
    for f in sorted(LOGS_DIR.glob("simulation_log_*.csv")):
        df = _read_csv(f)
        if not df.empty:
            df["_source"] = f.name
            frames.append(df)

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    return combined


# -----------------------------------------------------------------
# Chart helpers
# -----------------------------------------------------------------

COLORS = {
    "baseline": "#F87171",
    "athena":   "#34D399",
    "primary":  "#38BDF8",
    "warn":     "#FBBF24",
    "violet":   "#A78BFA",
}


def _chart_layout(title: str, y_label: str, height: int = 220) -> dict:
    return dict(
        title=dict(text=title, font=dict(color="#F8FAFC", size=14)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.4)",
        margin=dict(l=10, r=10, t=36, b=10),
        height=height,
        xaxis=dict(title="Simulation Step",
                   gridcolor="rgba(255,255,255,0.06)", color="#94A3B8"),
        yaxis=dict(title=y_label,
                   gridcolor="rgba(255,255,255,0.06)", color="#94A3B8"),
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#F8FAFC"),
        showlegend=False,
    )


def line_fig(df, col, title, color, y_label):
    fig = go.Figure()
    if not df.empty and col in df.columns:
        fig.add_trace(go.Scatter(
            x=df.reset_index().index, y=df[col],
            mode="lines", name=title,
            line=dict(color=color, width=2.5, shape="spline"),
            hovertemplate=f"Step %{{x}}<br>{title}: %{{y:.2f}}<extra></extra>",
        ))
    fig.update_layout(**_chart_layout(title, y_label))
    return fig


def bar_compare(labels, base_vals, ath_vals, title, y_label):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Baseline", x=labels, y=base_vals,
        marker_color=COLORS["baseline"],
        hovertemplate="%{x}: %{y:.2f}<extra>Baseline</extra>",
    ))
    fig.add_trace(go.Bar(
        name="Athena AI", x=labels, y=ath_vals,
        marker_color=COLORS["athena"],
        hovertemplate="%{x}: %{y:.2f}<extra>Athena AI</extra>",
    ))
    layout_args = _chart_layout(title, y_label, height=300)
    layout_args.update(
        barmode="group",
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#F8FAFC"))
    )
    fig.update_layout(**layout_args)
    return fig


def pct_change(base_val, new_val):
    """Return % change from base_val to new_val (negative = reduction)."""
    if base_val == 0:
        return 0.0
    return (new_val - base_val) / abs(base_val) * 100


# -----------------------------------------------------------------
# KPI computation helpers
# -----------------------------------------------------------------

def mean_val(df, col, default=0.0):
    if df is None or df.empty or col not in df.columns:
        return default
    v = pd.to_numeric(df[col], errors="coerce").dropna()
    return float(v.mean()) if len(v) else default


def total_val(df, col, default=0.0):
    if df is None or df.empty or col not in df.columns:
        return default
    v = pd.to_numeric(df[col], errors="coerce").dropna()
    return float(v.sum()) if len(v) else default


def comfort_pct(df):
    """Fraction of steps where |PMV| <= 0.5."""
    if df is None or df.empty or "pmv" not in df.columns:
        return 0.0
    in_band = (df["pmv"].abs() <= 0.5).sum()
    return in_band / len(df) * 100


# Each EnergyPlus timestep is 10 minutes = 1/6 hour; W * (1/6 h) / 1000 = kWh
WH_PER_STEP = 1 / 6


# -----------------------------------------------------------------
# Main page
# -----------------------------------------------------------------

def render():
    st.markdown("""
<div class="hero-shell animate-in" style="margin-bottom:1rem;">
<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
<div>
<div class="section-label">Delivery Requirement 3</div>
<h1 class="hero-title" style="font-size:1.8rem;">Quantitative Savings Report</h1>
<div class="hero-subtitle">
        Proves % reductions in kWh consumed by Athena AI vs rule-based baseline
        while maintaining occupant thermal comfort (PMV in [-0.5, 0.5]).
</div>
</div>
<div class="status-row">
<div class="status-pill"><span class="status-dot live"></span>AUTO REFRESH</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

    # -- Load data ------------------------------------------------
    athena_df   = load_current()
    baseline_df = load_archived()

    # If there are no archived logs yet, fall back to splitting current data
    # by reasoning (fallback rows = baseline, real AI rows = Athena)
    if baseline_df.empty and not athena_df.empty:
        fallback_mask = (
            athena_df["reasoning"].str.contains("fallback|rule.based", na=False, case=False)
            | (athena_df["confidence"] <= 0.1)
        )
        baseline_df = athena_df[fallback_mask].copy()
        athena_df   = athena_df[~fallback_mask].copy()

    has_baseline = not baseline_df.empty
    has_athena   = not athena_df.empty

    if not has_athena:
        st.markdown("""
<div class="glass-card animate-in" style="padding:2rem;text-align:center;">
<div class="section-label">NO DATA</div>
<h3>Run the simulation first to generate telemetry data.</h3>
</div>
""", unsafe_allow_html=True)
        return

    # -- KPI computation ------------------------------------------
    base_elec_mean  = mean_val(baseline_df, "electricity") if has_baseline else 0.0
    ath_elec_mean   = mean_val(athena_df,   "electricity")

    base_elec_total = total_val(baseline_df, "electricity") if has_baseline else 0.0
    ath_elec_total  = total_val(athena_df,   "electricity")

    base_kwh  = base_elec_total * WH_PER_STEP / 1000
    ath_kwh   = ath_elec_total  * WH_PER_STEP / 1000
    kwh_saved = max(0.0, base_kwh - ath_kwh) if has_baseline else 0.0
    kwh_pct   = pct_change(base_kwh, ath_kwh) if has_baseline else 0.0

    base_comfort = comfort_pct(baseline_df) if has_baseline else 0.0
    ath_comfort  = comfort_pct(athena_df)

    base_reward  = mean_val(baseline_df, "reward") if has_baseline else 0.0
    ath_reward   = mean_val(athena_df,   "reward")
    reward_pct   = pct_change(base_reward, ath_reward) if has_baseline else 0.0

    ath_conf    = mean_val(athena_df, "confidence")

    n_baseline  = len(baseline_df) if has_baseline else 0
    n_athena    = len(athena_df)

    # -- Data source info -----------------------------------------
    archived_files = sorted(LOGS_DIR.glob("simulation_log_*.csv"))
    src_note = (
        f"Baseline from {len(archived_files)} archived run(s)"
        if archived_files else "Baseline: in-run fallback rows"
    )

    st.markdown(f"""
<div style="background:rgba(56,189,248,0.06);border:1px solid rgba(56,189,248,0.2);
     border-radius:12px;padding:0.6rem 1rem;margin-bottom:1rem;
     font-size:0.82rem;color:#94A3B8;">
<strong style="color:#38BDF8;">Data sources --</strong>
  {src_note} &nbsp;|&nbsp; Current run: <code>simulation_log.csv</code> ({n_athena} steps)
</div>
""", unsafe_allow_html=True)

    # -- KPI cards ------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)

    def kpi_card(col, title, value, sub, accent_rgb):
        with col:
            st.markdown(f"""
<div class="metric-card animate-in">
<div class="metric-top">
<div class="metric-label">{title}</div>
<div class="metric-icon-box"
         style="background:rgba({accent_rgb},0.12);border-color:rgba({accent_rgb},0.3);">
<svg width="16" height="16" fill="rgba({accent_rgb},0.9)" viewBox="0 0 24 24">
<path d="M12 2L2 7v10l10 5 10-5V7L12 2z"/>
</svg>
</div>
</div>
<div class="metric-value" style="font-size:1.6rem;">{value}</div>
<div class="metric-subtitle">{sub}</div>
</div>
""", unsafe_allow_html=True)

    kwh_color = "52,211,153" if kwh_pct <= 0 else "248,113,113"
    kpi_card(c1, "kWh Reduction",
             f"{abs(kwh_pct):.1f}% {'savings' if kwh_pct <= 0 else 'increase'}",
             f"Athena: {ath_kwh:,.1f} kWh vs Baseline: {base_kwh:,.1f} kWh",
             kwh_color)

    kpi_card(c2, "Energy Saved",
             f"{kwh_saved:,.0f} kWh",
             "Total electricity not consumed under AI control",
             "56,189,248")

    kpi_card(c3, "Comfort Adherence",
             f"{ath_comfort:.1f}%",
             f"Athena steps with PMV in [-0.5, 0.5] (Baseline: {base_comfort:.1f}%)",
             "52,211,153")

    kpi_card(c4, "AI Confidence",
             f"{ath_conf:.2f}",
             f"Avg decision confidence | Reward gain: {reward_pct:+.1f}%",
             "167,139,250")

    # -- Result Summary -------------------------------------------
    if not has_baseline:
        baseline_notice = (
            "<div style='padding:0.75rem;border-radius:10px;"
            "background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.25);"
            "font-size:0.85rem;color:#FBBF24;margin-top:0.75rem;'>"
            "<strong>Note:</strong> No archived baseline logs found yet. "
            "Run the simulation for a few minutes, then restart it once to create an archive. "
            "The comparison will populate automatically."
            "</div>"
        )
    else:
        baseline_notice = ""

    st.markdown(f"""
<div class="glass-card animate-in" style="margin-top:1rem;margin-bottom:1rem;">
<div class="section-label">Quantitative Proof</div>
<h3 class="section-title">Result Summary</h3>
<div style="margin-top:0.8rem;display:grid;grid-template-columns:1fr 1fr;gap:1rem;">

<div style="padding:1rem;border-radius:14px;
                background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.25);">
<div style="font-size:0.78rem;font-weight:800;color:#F87171;
                  text-transform:uppercase;margin-bottom:0.4rem;">
        Rule-Based Baseline ({n_baseline:,} steps)
</div>
<div style="font-size:0.9rem;color:#E2E8F0;line-height:1.6;">
        Mean electricity demand: <strong>{base_elec_mean:,.0f} W</strong><br>
        Total energy: <strong>{base_kwh:,.1f} kWh</strong><br>
        PMV comfort adherence: <strong>{base_comfort:.1f}%</strong><br>
        Mean reward: <strong>{base_reward:.4f}</strong>
</div>
</div>

<div style="padding:1rem;border-radius:14px;
                background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.25);">
<div style="font-size:0.78rem;font-weight:800;color:#34D399;
                  text-transform:uppercase;margin-bottom:0.4rem;">
        Athena AI Agent ({n_athena:,} steps)
</div>
<div style="font-size:0.9rem;color:#E2E8F0;line-height:1.6;">
        Mean electricity demand: <strong>{ath_elec_mean:,.0f} W</strong><br>
        Total energy: <strong>{ath_kwh:,.1f} kWh</strong><br>
        PMV comfort adherence: <strong>{ath_comfort:.1f}%</strong><br>
        Mean reward: <strong>{ath_reward:.4f}</strong>
</div>
</div>

</div>

<div style="margin-top:1rem;padding:0.85rem;border-radius:12px;
              background:rgba(56,189,248,0.08);border:1px solid rgba(56,189,248,0.25);
              font-size:0.92rem;color:#E2E8F0;line-height:1.6;">
<strong style="color:#38BDF8;">Conclusion:</strong>
    Athena AI {'reduced' if kwh_pct <= 0 else 'used'} building electricity consumption by
<strong style="color:#34D399;">{abs(kwh_pct):.1f}%</strong>
    ({kwh_saved:,.0f} kWh {'saved' if kwh_saved > 0 else 'difference'})
    compared to the rule-based baseline period, while maintaining occupant comfort
    within the PMV [-0.5, 0.5] band for
<strong style="color:#34D399;">{ath_comfort:.1f}%</strong>
    of AI-controlled timesteps.
</div>
  {baseline_notice}
</div>
""", unsafe_allow_html=True)

    # -- Telemetry charts -----------------------------------------
    st.markdown('<div class="section-label" style="margin-bottom:0.5rem;">Telemetry Comparison</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if has_baseline:
            st.plotly_chart(
                line_fig(baseline_df, "electricity", "Baseline Electricity (W)",
                         COLORS["baseline"], "Watts"),
                use_container_width=True, config={"displayModeBar": False})
            st.plotly_chart(
                line_fig(baseline_df, "pmv", "Baseline PMV",
                         COLORS["warn"], "PMV"),
                use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Baseline charts will appear once archived logs exist.")

    with col2:
        st.plotly_chart(
            line_fig(athena_df, "electricity", "Athena Electricity (W)",
                     COLORS["athena"], "Watts"),
            use_container_width=True, config={"displayModeBar": False})
        st.plotly_chart(
            line_fig(athena_df, "pmv", "Athena PMV",
                     COLORS["primary"], "PMV"),
            use_container_width=True, config={"displayModeBar": False})

    # -- Bar comparison -------------------------------------------
    if has_baseline:
        st.plotly_chart(
            bar_compare(
                ["Mean Electricity (W)", "Total kWh", "PMV Adherence (%)", "Mean Reward x1000"],
                [base_elec_mean, base_kwh, base_comfort, base_reward * 1000],
                [ath_elec_mean,  ath_kwh,  ath_comfort,  ath_reward  * 1000],
                "Baseline vs Athena AI -- Side-by-Side Comparison",
                "Value",
            ),
            use_container_width=True, config={"displayModeBar": False},
        )

    # -- Export ---------------------------------------------------
    st.markdown('<div class="section-label" style="margin:1rem 0 0.4rem;">Export</div>',
                unsafe_allow_html=True)

    export = pd.DataFrame({
        "metric": [
            "Baseline Steps", "Athena Steps",
            "Total Baseline kWh", "Total Athena kWh",
            "kWh Saved", "% kWh Change",
            "Baseline Comfort %", "Athena Comfort %",
            "Mean Baseline Reward", "Mean Athena Reward",
            "AI Confidence",
        ],
        "value": [
            n_baseline, n_athena,
            round(base_kwh, 2), round(ath_kwh, 2),
            round(kwh_saved, 2), round(kwh_pct, 2),
            round(base_comfort, 2), round(ath_comfort, 2),
            round(base_reward, 4), round(ath_reward, 4),
            round(ath_conf, 4),
        ],
    })

    csv_bytes = export.to_csv(index=False).encode("utf-8")
    st.download_button("Download savings_report.csv", csv_bytes,
                       "savings_report.csv", "text/csv")

    # Auto-save
    (LOGS_DIR / "savings_report.csv").write_text(
        export.to_csv(index=False), encoding="utf-8"
    )


render()
