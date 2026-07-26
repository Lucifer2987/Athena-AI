# 🏛️ Athena AI — Autonomous Building Energy Management System

> **Athena AI** is a closed-loop, AI-driven Building Energy Management System (BEMS) that uses a live **EnergyPlus** simulation, a **Qwen2.5 LLM** reasoning engine, and a **Model Context Protocol (MCP)** tool-use framework to autonomously optimise HVAC energy consumption while maintaining occupant thermal comfort.

---

## 📸 Dashboard Screenshots


### 🏢 Live Building Digital Twin

| Live Dashboard | Agent Pipeline |
<img width="1054" height="978" alt="image" src="https://github.com/user-attachments/assets/d3220f2b-e900-4dce-806c-af094c48f0e3" />


### 📈 Quantitative Savings Report

<img width="702" height="766" alt="image" src="https://github.com/user-attachments/assets/3e2fd590-435b-47f3-a2d4-d26a0a7e124f" />


---

## 🎯 Key Results

| Metric | Baseline (Rule-Based) | Athena AI | Improvement |
|---|---|---|---|
| **Total Energy Consumed** | ~265,485 kWh | ~14,751 kWh | **94.4% reduction** |
| **PMV Comfort Adherence** | 100.0% | 100.0% | Maintained ✅ |
| **Mean Control Reward** | 0.8486 | 0.8753 | **+3.2% gain** |
| **Average AI Confidence** | — | 0.93 | High certainty |

---

## 🧠 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  EnergyPlus Simulation                   │
│        (Building Physics + Thermal Dynamics Engine)       │
└────────────────────────┬────────────────────────────────┘
                         │  Sensors: Temp, PMV, Electricity
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Athena AI Agent  (runtime.py)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │  Sensors │→ │  Planner │→ │   LLM    │→ │ Safety │  │
│  │ (MCP)    │  │          │  │  Policy  │  │  Val.  │  │
│  └──────────┘  └──────────┘  └──────────┘  └───┬────┘  │
│                                                 │        │
│                                          set_temperature  │
└─────────────────────────────────────────────────────────┘
                         │  Writes telemetry row
                         ▼
              logs/simulation_log.csv   ← Communication Bus
                         │
                         │  Auto-refresh every 6s
                         ▼
┌─────────────────────────────────────────────────────────┐
│           Streamlit Dashboard  (dashboard.py)            │
│    Digital Twin  |  Agent Pipeline  |  Telemetry ROI    │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Athena AI/
├── energyplus/                  # Core AI Engine
│   ├── runtime.py               # Main control loop entry point
│   ├── agent.py                 # High-level agent orchestration
│   ├── decision_engine.py       # LLM + fallback decision logic
│   ├── llm_client.py            # Ollama / Qwen2.5 API client
│   ├── llm_policy.py            # LLM adapter & response parsing
│   ├── sensors.py               # EnergyPlus sensor reader (MCP)
│   ├── actuators.py             # EnergyPlus setpoint writer (MCP)
│   ├── safety_validator.py      # Hard PMV/Temp safety enforcement
│   ├── planner.py               # High-level strategy planner
│   ├── memory.py                # Rolling trajectory memory buffer
│   ├── reward.py                # Comfort + energy reward function
│   ├── logger.py                # CSV telemetry logger
│   ├── environment.py           # EnergyPlus environment wrapper
│   ├── state_builder.py         # Building state dictionary builder
│   ├── config.py                # Global configuration constants
│   └── mcp/                     # MCP tool definitions
│
├── dashboard/                   # Streamlit Frontend
│   ├── dashboard.py             # Live real-time dashboard (port 8501)
│   ├── savings_report.py        # Quantitative savings report (port 8502)
│   ├── components.py            # Reusable UI components
│   ├── styles.py                # CSS design system
│   └── utils.py                 # Data loading & computation helpers
│
├── logs/                        # Data & Models
│   ├── simulation_log.csv       # LIVE telemetry bus (auto-updated)
│   ├── savings_report.csv       # Baseline vs AI comparison data
│   └── baseline_building.idf   # EnergyPlus building model (IDF)
│
├── assets/                      # Screenshots for README
├── Athena_AI_Architecture.md    # Detailed system architecture doc
└── README.md                    # This file
```

---

## ⚙️ How It Works

### 1. Sensing (MCP Tools: `read_pmv`, `read_energy`)
Every simulation timestep (10 min of building time), the agent reads three live sensor values from EnergyPlus:
- **Zone Air Temperature (°C)** — Current indoor temperature
- **PMV Index** — Predicted Mean Vote comfort score (-3 to +3, target: -0.5 to 0.5)
- **Electricity Demand (W)** — Building HVAC power draw

### 2. Reasoning (Qwen2.5 LLM via Ollama)
The sensor values are packed into a structured JSON prompt and sent to the **Qwen2.5:7b** model running locally via Ollama. The LLM reasons about the optimal next temperature setpoint using:
- Current building state
- Last 3 steps of history
- Strategy constraints (PMV comfort band, energy minimisation)

### 3. Safety Validation
Before any command is executed, the **SafetyValidator** enforces hard physical boundaries:
- Temperature must remain between **20°C and 26°C**
- PMV index must remain within **[-0.5, 0.5]**

### 4. Actuation (MCP Tool: `set_temperature`)
The validated setpoint is written directly into the EnergyPlus simulation via the **EnergyManagementSystem (EMS) Actuator**, completing the closed-loop control cycle.

### 5. Logging & Dashboard
Every step writes a telemetry row to `logs/simulation_log.csv`. The Streamlit dashboard auto-refreshes every **6 seconds** to display the live simulation state.

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10+ |
| EnergyPlus | 24.x or 25.x |
| Ollama | Latest |
| Qwen2.5 Model | `qwen2.5:7b` |

### 1. Install Python Dependencies

```bash
pip install pyenergyplus streamlit streamlit-autorefresh plotly pandas requests
```

### 2. Install & Start Ollama with Qwen2.5

```bash
# Install Ollama from https://ollama.com
ollama pull qwen2.5:7b
ollama serve
```

### 3. Run the AI Simulation Backend

```bash
cd "p:\Athena AI"
python energyplus/runtime.py
```

### 4. Launch the Live Dashboard

Open a **new terminal** and run:

```bash
streamlit run dashboard/dashboard.py
```

Open your browser at 👉 **http://localhost:8501**

### 5. Launch the Savings Report (Optional)

Open a **third terminal** and run:

```bash
streamlit run dashboard/savings_report.py --server.port 8502
```

Open your browser at 👉 **http://localhost:8502**

---

## 🎛️ Configuration

Key parameters can be tuned in `energyplus/config.py`:

| Parameter | Default | Description |
|---|---|---|
| `TEMP_MIN` | 20.0 °C | Minimum allowed setpoint |
| `TEMP_MAX` | 26.0 °C | Maximum allowed setpoint |
| `PMV_COMFORT_LOW` | -0.5 | Lower PMV comfort boundary |
| `PMV_COMFORT_HIGH` | +0.5 | Upper PMV comfort boundary |
| `LLM_MODEL` | `qwen2.5:7b` | Ollama model to use |
| `LLM_TIMEOUT` | 45s | Per-request LLM timeout |

---

## 🧩 Technology Stack

| Layer | Technology |
|---|---|
| **Building Simulation** | EnergyPlus v24/25 via Python API |
| **AI Reasoning Engine** | Qwen2.5 7B (via Ollama, local inference) |
| **Agent Framework** | Custom MCP (Model Context Protocol) |
| **Frontend Dashboard** | Streamlit + Plotly |
| **Communication Bus** | CSV file (simulation_log.csv) |
| **Safety Layer** | Rule-based hard constraint validator |
| **Language** | Python 3.10+ |

---

## 📊 Deliverables

- ✅ **Fully Functional Source Code** — Unified Python codebase managing EnergyPlus API wrapper, LLM agent orchestration, and communication bus.
- ✅ **Building Models (.idf files)** — Baseline `baseline_building.idf` stored in `logs/`, with runtime-modified versions generated per session in `simulations/`.
- ✅ **Quantitative Savings Dashboard** — Visual dashboard proving **94.4% kWh reduction** vs baseline while maintaining **100% PMV comfort adherence**.

---

## Author 

Prakhar Shrivastava
