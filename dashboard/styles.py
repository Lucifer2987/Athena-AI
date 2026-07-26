def load_css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-dark: #070B14;
    --panel-bg: rgba(15, 23, 42, 0.72);
    --panel-border: rgba(56, 189, 248, 0.16);
    --panel-glow: rgba(56, 189, 248, 0.06);

    --primary: #38BDF8;
    --primary-glow: rgba(56, 189, 248, 0.3);
    --success: #34D399;
    --success-glow: rgba(52, 211, 153, 0.25);
    --warning: #FBBF24;
    --warning-glow: rgba(251, 191, 36, 0.25);
    --danger: #F87171;
    --danger-glow: rgba(248, 113, 113, 0.25);
    --violet: #A78BFA;
    --violet-glow: rgba(167, 139, 250, 0.25);

    --text-main: #F8FAFC;
    --text-muted: #94A3B8;
    --text-dim: #64748B;
}

/* Global Reset & Background */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-main);
    background-color: var(--bg-dark) !important;
}

.stApp {
    background: 
        radial-gradient(circle at 12% 8%, rgba(56, 189, 248, 0.08), transparent 35%),
        radial-gradient(circle at 88% 12%, rgba(52, 211, 153, 0.06), transparent 32%),
        radial-gradient(circle at 50% 85%, rgba(167, 139, 250, 0.05), transparent 40%),
        linear-gradient(180deg, #070B14 0%, #0B132B 100%) !important;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1680px !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: rgba(7, 11, 20, 0.5);
}
::-webkit-scrollbar-thumb {
    background: rgba(56, 189, 248, 0.25);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(56, 189, 248, 0.45);
}

/* Hide Streamlit Chrome */
header, footer, #MainMenu {
    visibility: hidden;
    height: 0;
}

/* Keyframes */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 15px var(--primary-glow); }
    50% { box-shadow: 0 0 28px var(--primary-glow), 0 0 10px rgba(56, 189, 248, 0.4); }
}

@keyframes liveDot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.35; transform: scale(0.85); }
}

@keyframes buildingPulse {
    0%, 100% { filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.25)); }
    50% { filter: drop-shadow(0 0 16px rgba(56, 189, 248, 0.55)); }
}

.animate-in {
    animation: fadeIn 0.35s ease-out forwards;
}

/* Hero Shell */
.hero-shell {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.88), rgba(11, 19, 43, 0.96));
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--panel-border);
    border-radius: 20px;
    padding: 1.25rem 1.6rem;
    box-shadow: 
        0 16px 36px rgba(0, 0, 0, 0.4),
        0 0 30px var(--panel-glow);
}

.hero-shell::after {
    content: "";
    position: absolute;
    top: 0; right: 0; width: 320px; height: 100%;
    background: radial-gradient(circle at 100% 0%, rgba(56, 189, 248, 0.1), transparent 70%);
    pointer-events: none;
}

.hero-brand {
    display: flex;
    align-items: center;
    gap: 1.1rem;
}

.athena-logo-box {
    width: 56px;
    height: 56px;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.22), rgba(167, 139, 250, 0.12));
    border: 1.5px solid rgba(56, 189, 248, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 22px rgba(56, 189, 248, 0.25);
    flex-shrink: 0;
}

.hero-title {
    font-size: clamp(1.6rem, 2.4vw, 2.2rem);
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 0;
    line-height: 1.1;
    background: linear-gradient(135deg, #FFFFFF 30%, var(--primary) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    color: var(--text-muted);
    font-size: 0.88rem;
    margin-top: 0.25rem;
    max-width: 840px;
    line-height: 1.45;
}

.status-row {
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
    align-items: center;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.45rem 0.85rem;
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(8px);
    color: var(--text-main);
    font-size: 0.8rem;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--success);
    box-shadow: 0 0 8px var(--success-glow);
    animation: liveDot 2s ease-in-out infinite;
}

.status-dot.live {
    background: var(--primary);
    box-shadow: 0 0 10px var(--primary-glow);
}

.status-dot.offline {
    background: var(--text-dim);
    box-shadow: none;
    animation: none;
}

/* Glass Card */
.glass-card {
    position: relative;
    overflow: hidden;
    background: var(--panel-bg);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid var(--panel-border);
    border-radius: 18px;
    padding: 1.2rem;
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.04);
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.glass-card:hover {
    border-color: rgba(56, 189, 248, 0.32);
    box-shadow: 0 14px 32px rgba(0, 0, 0, 0.35), 0 0 20px rgba(56, 189, 248, 0.1);
}

/* Metric Cards */
.metric-card {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.82), rgba(20, 30, 55, 0.72));
    backdrop-filter: blur(12px);
    border: 1px solid var(--panel-border);
    border-radius: 16px;
    padding: 1rem 1.15rem;
    box-shadow: 0 8px 22px rgba(0, 0, 0, 0.25);
    transition: all 0.2s ease;
    height: 100%;
}

.metric-card:hover {
    transform: translateY(-2px);
    border-color: rgba(56, 189, 248, 0.38);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35), 0 0 18px rgba(56, 189, 248, 0.12);
}

.metric-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}

.metric-label {
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.metric-icon-box {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.22);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    color: var(--primary);
    flex-shrink: 0;
}

.metric-value-row {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.metric-value {
    font-size: clamp(1.4rem, 1.9vw, 1.9rem);
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--text-main);
    line-height: 1.1;
}

.metric-delta {
    font-size: 0.76rem;
    font-weight: 700;
    padding: 0.18rem 0.5rem;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    gap: 0.2rem;
}

.metric-delta.up {
    background: rgba(52, 211, 153, 0.14);
    color: var(--success);
    border: 1px solid rgba(52, 211, 153, 0.25);
}

.metric-delta.down {
    background: rgba(248, 113, 113, 0.14);
    color: var(--danger);
    border: 1px solid rgba(248, 113, 113, 0.25);
}

.metric-delta.neutral {
    background: rgba(148, 163, 184, 0.12);
    color: var(--text-muted);
    border: 1px solid rgba(148, 163, 184, 0.18);
}

.metric-subtitle {
    margin-top: 0.4rem;
    font-size: 0.78rem;
    color: var(--text-muted);
    line-height: 1.35;
}

/* Section Header */
.section-label {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
    background: rgba(56, 189, 248, 0.1);
    border: 1px solid rgba(56, 189, 248, 0.22);
    color: var(--primary);
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.section-title {
    font-size: clamp(1.15rem, 1.6vw, 1.4rem);
    font-weight: 800;
    margin: 0.25rem 0 0;
    letter-spacing: -0.02em;
    color: var(--text-main);
}

.section-description {
    margin-top: 0.2rem;
    color: var(--text-muted);
    font-size: 0.85rem;
    line-height: 1.4;
}

/* Digital Twin Component */
.twin-building-container {
    position: relative;
    min-height: 420px;
    border-radius: 18px;
    background: 
        radial-gradient(circle at 50% 20%, rgba(56, 189, 248, 0.08), transparent 50%),
        linear-gradient(180deg, rgba(10, 16, 30, 0.95), rgba(7, 11, 20, 0.98));
    border: 1px solid var(--panel-border);
    padding: 1.25rem;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.3);
}

.building-schematic {
    position: relative;
    height: 230px;
    margin: 0.8rem 0;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    gap: 1.2rem;
}

.schematic-zone {
    position: relative;
    border-radius: 12px 12px 4px 4px;
    border: 1.5px solid rgba(56, 189, 248, 0.3);
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.9), rgba(11, 19, 36, 0.95));
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    padding: 0.6rem;
    transition: all 0.3s ease;
}

.schematic-zone.core {
    width: 150px;
    height: 210px;
    border-color: rgba(56, 189, 248, 0.5);
    box-shadow: 0 0 30px rgba(56, 189, 248, 0.15);
    animation: buildingPulse 4s ease-in-out infinite;
}

.schematic-zone.perimeter {
    width: 110px;
    height: 160px;
    border-color: rgba(167, 139, 250, 0.4);
}

.zone-header-tag {
    font-size: 0.7rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--primary);
    text-align: center;
}

.zone-window-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 5px;
    padding: 0.2rem;
}

.zone-window {
    aspect-ratio: 1;
    border-radius: 4px;
    background: rgba(56, 189, 248, 0.15);
    border: 1px solid rgba(56, 189, 248, 0.25);
    transition: all 0.3s ease;
}

.zone-window.lit {
    background: rgba(52, 211, 153, 0.35);
    border-color: var(--success);
    box-shadow: 0 0 8px var(--success-glow);
}

.air-flow-indicator {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 100%;
    height: 100%;
    pointer-events: none;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.12) 0%, transparent 70%);
}

.twin-stat-tile {
    padding: 0.7rem 0.85rem;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.025);
    border: 1px solid rgba(255, 255, 255, 0.06);
    text-align: center;
}

.twin-stat-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
}

.twin-stat-val {
    font-size: 0.98rem;
    font-weight: 800;
    color: var(--text-main);
    margin-top: 0.15rem;
}

/* Agent Workflow Stepper */
.workflow-pipeline {
    display: flex;
    flex-direction: column;
    gap: 0.55rem;
}

.workflow-node {
    display: grid;
    grid-template-columns: 34px 1fr auto;
    gap: 0.75rem;
    align-items: center;
    padding: 0.65rem 0.85rem;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    transition: all 0.2s ease;
}

.workflow-node.active {
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.14), rgba(15, 23, 42, 0.85));
    border-color: rgba(56, 189, 248, 0.42);
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.15);
}

.workflow-node.completed {
    border-color: rgba(52, 211, 153, 0.28);
    background: rgba(52, 211, 153, 0.04);
}

.node-number {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.05);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.82rem;
    color: var(--text-muted);
}

.workflow-node.active .node-number {
    background: var(--primary);
    color: #070B14;
    box-shadow: 0 0 12px var(--primary-glow);
}

.workflow-node.completed .node-number {
    background: rgba(52, 211, 153, 0.2);
    color: var(--success);
}

.node-title {
    font-size: 0.88rem;
    font-weight: 700;
    color: var(--text-main);
}

.node-desc {
    font-size: 0.76rem;
    color: var(--text-muted);
    line-height: 1.3;
}

.node-status-badge {
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.18rem 0.5rem;
    border-radius: 999px;
    text-transform: uppercase;
}

.node-status-badge.active {
    background: rgba(56, 189, 248, 0.2);
    color: var(--primary);
    border: 1px solid rgba(56, 189, 248, 0.35);
}

.node-status-badge.done {
    background: rgba(52, 211, 153, 0.2);
    color: var(--success);
    border: 1px solid rgba(52, 211, 153, 0.35);
}

.node-status-badge.pending {
    background: rgba(148, 163, 184, 0.1);
    color: var(--text-dim);
}

/* Decision Panel */
.decision-card {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.88), rgba(11, 19, 43, 0.96));
    border: 1px solid var(--panel-border);
    border-radius: 18px;
    padding: 1.25rem;
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.3);
}

.decision-tile {
    padding: 0.8rem 0.95rem;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.025);
    border: 1px solid rgba(255, 255, 255, 0.06);
    height: 100%;
}

.decision-kicker {
    font-size: 0.7rem;
    font-weight: 800;
    color: var(--primary);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.25rem;
}

.decision-val {
    font-size: 0.98rem;
    font-weight: 700;
    color: var(--text-main);
    line-height: 1.4;
}

.reasoning-box {
    margin-top: 1rem;
    padding: 1.1rem;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.05), rgba(167, 139, 250, 0.03));
    border: 1px solid rgba(56, 189, 248, 0.2);
}

.reasoning-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.5rem;
}

.reasoning-avatar {
    width: 32px;
    height: 32px;
    border-radius: 9px;
    background: rgba(56, 189, 248, 0.15);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.95rem;
    color: var(--primary);
    flex-shrink: 0;
}

.reasoning-text {
    color: #E2E8F0;
    font-size: 0.9rem;
    line-height: 1.55;
    font-weight: 400;
}

/* System Health Badges */
.health-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 0.75rem;
}

.health-card {
    padding: 0.8rem 0.95rem;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.06);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.health-name {
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--text-muted);
}

.health-status-tag {
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.2rem 0.55rem;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
}

.health-status-tag.good {
    background: rgba(52, 211, 153, 0.14);
    color: var(--success);
    border: 1px solid rgba(52, 211, 153, 0.25);
}

.health-status-tag.warn {
    background: rgba(251, 191, 36, 0.14);
    color: var(--warning);
    border: 1px solid rgba(251, 191, 36, 0.25);
}

/* Plotly Chart Card Wrap */
.chart-card-wrap {
    position: relative;
    border-radius: 16px;
    background: var(--panel-bg);
    border: 1px solid var(--panel-border);
    padding: 0.75rem 0.75rem 0.4rem;
    backdrop-filter: blur(14px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
}

.chart-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.2rem 0.4rem 0.6rem;
}

.chart-card-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--text-main);
}

.chart-card-badge {
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.25);
    color: var(--primary);
}
</style>
"""
