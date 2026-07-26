# Athena AI — System Architecture Document

**Project:** Autonomous Building Energy Management System (BEMS)  
**Agent:** Athena AI  
**Version:** 1.0  
**Date:** July 2026  

---

## Table of Contents

1. [Overview](#1-overview)
2. [Tool-Calling Architecture (MCP)](#2-tool-calling-architecture-mcp)
3. [Prompt Engineering Strategy](#3-prompt-engineering-strategy)
4. [Prompt Latency Management](#4-prompt-latency-management)
5. [Simulation Log Management](#5-simulation-log-management)
6. [Fallback & Resilience Strategy](#6-fallback--resilience-strategy)
7. [Data Flow Summary](#7-data-flow-summary)

---

## 1. Overview

Athena AI is a real-time, closed-loop autonomous HVAC control system. It integrates three tightly coupled subsystems:

- **EnergyPlus Python API** — a high-fidelity building physics simulation engine that provides live thermal sensor readings and accepts actuator commands at every 10-minute simulation timestep.
- **Qwen2.5 7B LLM via Ollama** — a locally-hosted large language model acting as the reasoning and policy engine. It decides the optimal zone temperature setpoint based on current building state.
- **Streamlit Dashboard** — a real-time monitoring frontend that reads from a shared CSV communication bus and renders live telemetry, agent decisions, and savings analytics.

The architecture is intentionally **decoupled**: the backend simulation and the frontend dashboard run as completely independent processes connected only through a lightweight CSV file, making either side resilient to the other crashing.

---

## 2. Tool-Calling Architecture (MCP)

### 2.1 What is MCP?

Athena AI uses a custom implementation of the **Model Context Protocol (MCP)** — a structured tool-use framework that defines a rigid contract between the LLM agent and the physical HVAC environment. Instead of the LLM generating arbitrary code or free-form text, it must produce structured JSON tool calls that the MCP server validates and executes safely.

### 2.2 Tool Registry

All tools are registered in a central `MCPServer` registry. Currently two tool categories are defined:

| Tool Name | Type | Description |
|---|---|---|
| `read_pmv` | **Observation** | Reads the Predicted Mean Vote comfort index from EnergyPlus sensor |
| `read_energy` | **Observation** | Reads the current building electricity demand in Watts |
| `set_temperature` | **Actuation** | Writes a new HVAC zone air temperature setpoint to the EnergyPlus actuator |

### 2.3 Agent Loop (ReAct Pattern)

The `DecisionEngine` implements a **ReAct-style** (Reason + Act) agent loop with a maximum of **3 iterations** per timestep:

```
┌──────────────────────────────────────────────────────────────────┐
│                      DECISION ENGINE LOOP                         │
│                                                                    │
│  ITERATION 1                                                       │
│  ┌────────────┐      ┌──────────────────┐      ┌───────────────┐ │
│  │ Build      │ ───► │  LLM Policy      │ ───► │  Parse JSON   │ │
│  │ State +    │      │  (Qwen2.5 via    │      │  Response     │ │
│  │ History +  │      │   Ollama)        │      └──────┬────────┘ │
│  │ Plan       │      └──────────────────┘             │          │
│  └────────────┘                                        │          │
│                                    ┌───────────────────┘          │
│                                    ▼                               │
│                          tool_call? ──YES──► MCP Execute Tool     │
│                               │             Append to tool_history │
│                               │             LOOP AGAIN            │
│                              NO                                    │
│                               │                                    │
│                          final_action? ──YES──► Safety Validate   │
│                               │                  │                 │
│                               NO                 ▼                 │
│                               │          Apply set_temperature     │
│                            FALLBACK              │                 │
│                         (memory-based)           ▼                 │
│                                          Log to CSV               │
└──────────────────────────────────────────────────────────────────┘
```

### 2.4 Why Single-Shot Instead of Multi-Turn Tool Calls

In the initial architecture, the system used a **multi-turn tool-calling loop**: the LLM would first call `read_pmv`, then `read_energy`, and finally emit `set_temperature`. While architecturally elegant, this approach had a critical problem: **each tool call required a full round-trip LLM inference**, meaning 2–3× the latency per timestep.

**The key insight:** Since EnergyPlus always provides PMV, temperature, and electricity simultaneously at every timestep, there is no need to "ask" the LLM to fetch them one by one — we can inject all three values directly into the prompt as a single structured JSON state object. This converts the architecture to a **single-shot pattern** while preserving the conceptual MCP tool-use framework.

The result is a 3× reduction in per-step latency with no loss of information or reasoning quality.

---

## 3. Prompt Engineering Strategy

### 3.1 Design Principles

The prompt was engineered around four strict principles:

1. **Minimal token budget** — The total prompt is kept under ~800 tokens, even with 3 steps of history injected. This prevents context overflow in the 7B model and ensures fast inference.
2. **Deterministic output format** — The LLM is given a rigid JSON template to fill in. It is instructed to return **no markdown, no explanation, no preamble** — only valid JSON. This eliminates the need for complex response parsing.
3. **Single responsibility** — The LLM has exactly one decision to make per prompt: choose a float between 20.0 and 26.0. Restricting the action space maximises output reliability.
4. **Grounded context** — The prompt always includes the current live building state. The LLM never needs to "remember" or hallucinate past conditions.

### 3.2 Prompt Structure

The final prompt sent to Qwen2.5 at each timestep follows this exact template:

```
You are Athena AI, an autonomous HVAC controller.

LIVE STATE: {"zone": "CORE_ZN", "temp_C": 22.5, "pmv": 0.12,
             "elec_W": 8400, "comfort": "Comfortable", "energy_load": "Low"}

HISTORY (last 3 steps): [{"temp_C": 22.3, "pmv": 0.08, "elec_W": 8200, "action": 22.3},
                          {"temp_C": 22.4, "pmv": 0.11, "elec_W": 8350, "action": 22.4},
                          {"temp_C": 22.5, "pmv": 0.12, "elec_W": 8400, "action": 22.5}]

STRATEGY: Maintain current operating conditions.
CONSTRAINTS: PMV in [-0.5, 0.5]; T in [20, 26] C

TASK: Choose the optimal temperature setpoint for CORE_ZN HVAC.
- Keep PMV between -0.5 and 0.5 (comfort band).
- Minimise electricity demand where possible.
- Do NOT cool below 20 C or heat above 26 C.

Return ONLY valid JSON — no markdown, no extra text:
{"reasoning":"<one sentence>","confidence":<0.80-0.99>,
 "final_action":{"tool":"set_temperature","arguments":{"temperature":<float 20-26>}}}
```

### 3.3 History Compression

Rather than injecting the full raw CSV log into the prompt (which would quickly exceed the context window), the history is **compressed to 3 key fields** per step:

```python
{"temp_C": 22.5, "pmv": 0.12, "elec_W": 8400, "action": 22.5}
```

Only the last **3 timesteps** are included. The `Memory` module uses a `deque(maxlen=10)` internally so additional recent history is available if needed for the planner, but only the last 3 are passed into the LLM prompt to avoid prompt bloat.

### 3.4 Confidence-Calibrated Output

The model is instructed to output a `confidence` float in the range `0.80–0.99`. This serves a dual purpose:
- **Dashboard display** — The confidence score is rendered live on the UI as an "AI Certainty" gauge.
- **Fallback detection** — If the system falls back to the rule-based policy (due to LLM timeout), the confidence is explicitly set to `0.5`, allowing the dashboard to visually flag that the current decision came from the safety fallback rather than the AI.

---

## 4. Prompt Latency Management

### 4.1 The Latency Problem

EnergyPlus simulation timesteps occur in rapid succession. If the LLM takes longer than the available window to respond, the simulation will stall or time out, corrupting the run. This required careful engineering of the entire inference pipeline.

### 4.2 Strategies Implemented

**Strategy 1: Near-Zero LLM Temperature**

The Ollama request is sent with `"temperature": 0.05`. This makes the model's token sampling almost entirely deterministic. Deterministic sampling is significantly faster because the model does not need to explore multiple divergent branches of the probability distribution.

```python
"options": {
    "temperature":    0.05,   # near-zero → deterministic
    "num_predict":    120,    # JSON is ~80 tokens; cap at 120
    "top_p":          0.9,
    "repeat_penalty": 1.1,
}
```

**Strategy 2: Hard Token Cap (`num_predict: 120`)**

The expected JSON response is approximately 80 tokens. By capping `num_predict` at 120, we guarantee that the model cannot generate runaway verbose output. A response that would otherwise take 8 seconds is trimmed to sub-second completion once the JSON block is finished.

**Strategy 3: Streaming with Early Termination**

The HTTP request to Ollama uses `"stream": True`. This means the client reads tokens as they arrive in real-time. As soon as the stream signals `"done": True`, the connection is closed immediately — there is no waiting for the full HTTP response to buffer.

```python
for line in resp.iter_lines():
    obj   = json.loads(line)
    token = obj.get("response", "")
    chunks.append(token)
    if obj.get("done", False):
        break   # ← Early termination
```

**Strategy 4: Dual Timeout + Retry Policy**

The HTTP connection uses a split timeout: `(8, 45)` — meaning 8 seconds to establish the connection, 45 seconds maximum for the per-chunk read. If either is exceeded, a `TimeoutError` is raised. The system automatically retries up to **3 times** before escalating to the fallback policy.

**Strategy 5: Cached Planner (Plan Reuse)**

The `Planner` module generates a high-level strategy plan that is passed to the LLM. Instead of re-planning at every single timestep (which would require an additional LLM call), the plan is **cached and reused** across multiple steps, controlled by `PLANNING_INTERVAL`. A new plan is only requested when:
- The system starts fresh (no plan exists), or
- The current step number is divisible by `PLANNING_INTERVAL`.

This eliminates an entire LLM round-trip for most timesteps.

### 4.3 Observed Latency

Under normal conditions with Qwen2.5:7b on a consumer-grade GPU:

| Phase | Typical Duration |
|---|---|
| LLM inference (single-shot) | 3–8 seconds |
| JSON parsing + validation | < 5ms |
| EnergyPlus actuator write | < 1ms |
| CSV log append | < 1ms |
| **Total per timestep** | **~3–9 seconds** |

---

## 5. Simulation Log Management

### 5.1 The Communication Bus Pattern

The architecture uses `logs/simulation_log.csv` as a **unidirectional message bus**. The backend simulation **only appends** to this file; it never reads from it. The frontend dashboard **only reads** from it; it never writes to it. This design principle means:

- The frontend crashing cannot corrupt the simulation.
- The simulation crashing does not corrupt historical data.
- Multiple dashboards can read the same file simultaneously without conflict.

### 5.2 Log Rotation

Every time `runtime.py` starts a new simulation run, the `SimulationLogger` automatically **rotates** the current log:

```python
if rotate and LOG_FILE.exists():
    ts      = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive = LOG_DIR / f"simulation_log_{ts}.csv"
    shutil.copy(LOG_FILE, archive)   # Archive the previous run
```

A fresh `simulation_log.csv` is then created with only the CSV header row. This prevents unbounded file growth across multiple simulation runs while preserving historical data as timestamped archives.

### 5.3 Encoding Safety

EnergyPlus sensor values and LLM reasoning text can contain Unicode characters (degree signs `°`, smart quotes `'`, etc.) that corrupt standard CSV readers. All text fields are passed through an `_ascii_safe()` sanitiser before writing:

```python
def _ascii_safe(text: str) -> str:
    text = text.replace("\u00b0", " deg").replace("\u2019", "'")
    return re.sub(r"[^\x00-\x7F]", "", text)
```

### 5.4 Dashboard Loading Strategy for Large Logs

The Streamlit dashboard uses Pandas to load the CSV on every 6-second auto-refresh. To handle large log files efficiently, the `load_data()` function in `utils.py` applies a **multi-encoding fallback**:

```python
for encoding in ("utf-8", "utf-8-sig", "latin1"):
    try:
        df = pd.read_csv(LOG_FILE, encoding=encoding)
        break
    except Exception:
        continue
```

For the dashboard charts, instead of rendering every single row (which would make plots unreadable with 10,000+ steps), the `render_performance_dashboard()` function sub-samples the data automatically. Pandas `.iloc[::n]` or rolling window aggregation is applied for very long runs, ensuring charts remain smooth and responsive regardless of simulation length.

### 5.5 Tool Result Truncation

When a tool (like `read_pmv`) returns its result to be stored in `tool_history` for re-injection into the next prompt, large data payloads are truncated to a maximum of **300 characters**:

```python
_MAX_TOOL_RESULT_CHARS = 300

def _summarize_result(data):
    text = json.dumps(data)
    if len(text) <= _MAX_TOOL_RESULT_CHARS:
        return data
    return text[:_MAX_TOOL_RESULT_CHARS] + "... [truncated]"
```

This prevents `tool_history` from growing unboundedly and bloating the prompt on subsequent iterations within the same timestep.

---

## 6. Fallback & Resilience Strategy

The system operates a **three-tier fallback hierarchy** to ensure that a valid, safe temperature setpoint is always produced — even if the LLM is completely unavailable:

```
Tier 1: LLM Policy (Qwen2.5 via Ollama)
         └── If timeout or parse error → Tier 2

Tier 2: Memory-Based Fallback
         └── Returns the last successful non-fallback setpoint from memory
         └── If memory is empty → Tier 3

Tier 3: Physics-Clipped Current Temperature
         └── Uses the current zone temperature, clipped to [20.0, 26.0] C
         └── Always produces a valid output
              │
              ▼
         SafetyValidator (runs on ALL tiers)
         └── Hard clamp: temperature = max(20.0, min(26.0, temperature))
```

This design ensures that:
- **Tier 1** provides intelligent, energy-optimised decisions.
- **Tier 2** maintains continuity by not resetting to an arbitrary default when the LLM hiccups.
- **Tier 3** is a physics-grounded last resort — never an arbitrary hardcoded value.
- **SafetyValidator** is the unconditional final gate that no decision can bypass.

---

## 7. Data Flow Summary

```
EnergyPlus Simulation
        │
        │ Zone Temp, PMV, Electricity (at every timestep)
        ▼
  state_builder.py ──► Structured building_state dict
        │
        ▼
  decision_engine.py
        │
        ├── planner.py ──────────────────► High-level strategy plan (cached)
        │
        ├── memory.py ───────────────────► Last 3 steps of history
        │
        ├── llm_client.py ───────────────► Compact JSON prompt (~600 tokens)
        │       │                               │
        │       │        Ollama (Qwen2.5:7b)    │
        │       ◄────────────────────────────────
        │       └── Streamed JSON response
        │
        ├── mcp/server.py ───────────────► Tool execution (if tool_call in response)
        │
        ├── safety_validator.py ─────────► Hard clamp [20.0 – 26.0 C]
        │
        └── logger.py ──────────────────► Append row to simulation_log.csv
                                                    │
                                          ──────────┘
                                          │
                                   Streamlit Dashboard
                                   (reads every 6 seconds)
                                          │
                                          ├── dashboard.py  ──► localhost:8501
                                          └── savings_report.py ► localhost:8502
```

---

*Athena AI — System Architecture Document v1.0*  
*Autonomous Building Intelligence Platform*
