# Athena AI — Agentic Building Energy Management System

## Project Overview

**Athena AI** is an Agentic Building Energy Management System (BEMS) built on top of EnergyPlus.

Instead of using hardcoded rules, Athena behaves like an autonomous AI agent. Its job is to:

- Monitor building conditions
- Reason about comfort and energy
- Use tools to gather information
- Decide the best HVAC temperature
- Apply the action to EnergyPlus
- Learn from previous decisions

The project combines:

- EnergyPlus Runtime API
- MCP (Model Context Protocol)
- Local LLM (Qwen2.5 via Ollama)
- Memory
- Planning
- Safety Validation
- Streamlit Dashboard
- CSV Logging

---

## High-Level Architecture

```
                    EnergyPlus Simulation
                              │
                              ▼
                    callback(control_loop)
                              │
                              ▼
                  EnergyPlusEnvironment
                              │
                              ▼
                     Building Observation
                              │
                              ▼
                     Decision Engine
                              │
      ┌───────────────────────┼────────────────────────┐
      │                       │                        │
      ▼                       ▼                        ▼
 Planner                 Memory                  LLM Policy
                                                    │
                                                    ▼
                                               LLM Client
                                                    │
                                             Ollama (Qwen)
                                                    │
                                            JSON Response
                                                    │
                                                    ▼
                           MCP Server → MCP Registry → Tool
                                                    │
                                                    ▼
                           Sensor / Memory / Actuator
                                                    │
                                                    ▼
                                           Tool Result
                                                    │
                                                    ▼
                                       Decision Engine Loop
                                                    │
                                                    ▼
                                       Safety Validator
                                                    │
                                                    ▼
                                        Apply Temperature
                                                    │
                                                    ▼
                                          EnergyPlus Actuator
                                                    │
                                                    ▼
                                            Logger + Memory
```

---

## Complete Runtime Flow

### 1. `runtime.py`

This is the entry point. It creates:

- EnergyPlus API
- Environment
- Sensors
- Actuators
- DecisionEngine
- Registry
- Tools
- Logger

Then registers callbacks:

- `callback_begin_new_environment()`
- `callback_begin_system_timestep_before_predictor()`

EnergyPlus automatically calls these.

### 2. `begin_environment()`

Runs once. Responsibilities:

- Initialize Sensors
- Initialize Actuators
- Register every MCP Tool, e.g.:
  - `read_temperature`
  - `read_pmv`
  - `read_energy`
  - `get_recent_history`
  - `set_temperature`

After this, the Registry knows every available tool.

### 3. `control_loop()`

Runs every timestep.

**Flow:**

```
Observation → Building State → Decision Engine → Temperature
→ Reward → Logger → Apply Action → Store Transition
```

---

## Environment Layer

Environment converts raw EnergyPlus data into AI-friendly information.

**Raw:**
- temperature
- electricity
- PMV

**↓ becomes Building State:**

```json
{
  "temperature": 21.8,
  "electricity": 0,
  "pmv": 0,
  "comfort_status": "Comfortable",
  "energy_status": "Low"
}
```

> Decision Engine never directly touches EnergyPlus — it only sees Building State.

---

## Decision Engine

The Decision Engine is the brain. Responsibilities:

- Planning
- Agent Loop
- Tool Execution
- Safety
- Memory

### Step 1 — Collect Memory

```python
history = memory.get_history()
```

### Step 2 — Planner

Every few timesteps, `Planner.create_plan()` returns:

- Goal
- Strategy
- Constraints

**Example:**
- Maintain comfort
- Reduce energy
- Keep PMV between -0.5 and 0.5

The plan is cached.

### Step 3 — Initialize Agent

```python
tool_history = []
executed_tools = set()
```

### Step 4 — Agent Loop

Maximum **5 iterations**. Every iteration:

```
LLM → Tool → LLM → Tool → LLM → Final Action
```

---

## LLM Policy

Decision Engine never talks directly to Ollama. Instead:

```
Decision Engine → LLM Policy → LLM Client
```

LLM Policy is a wrapper. It:

- Calls LLM Client
- Validates JSON
- Separates `tool_call` or `final_action`

---

## LLM Client

Builds the prompt. Prompt contains:

- Current Building State
- Recent Memory
- Current Plan
- Tool History
- Available Tools
- Rules
- Workflow

Then:

```
requests.post() → localhost:11434 → Qwen2.5 → Returns JSON
```

---

## Tool History

Every executed tool is appended, e.g.:

```json
{
  "tool": "read_pmv",
  "result": 0.1
}
```

**Example sequence:**

```
[read_pmv, read_energy]
```

This history is sent back to the LLM every iteration.

**Purpose:** Avoid duplicate tool calls.

---

## MCP Architecture

Decision Engine never calls tools directly. Instead:

```
Decision Engine → MCP Server → Registry → Actual Tool
```

### MCP Registry

Registry stores:

```
Tool Name → Function Pointer → Description
```

**Example:**
```
read_pmv → EnergyPlusTools.read_pmv()
```

### MCP Server

Receives `execute("read_pmv")`, calls Registry, and returns a `ToolResult`:

```json
{
  "success": true,
  "data": "...",
  "message": "..."
}
```

---

## EnergyPlus Tools

Contains actual implementations:

| Tool | Maps to |
|---|---|
| `read_temperature()` | `Observation.temperature` |
| `read_energy()` | `Observation.electricity` |
| `read_pmv()` | `Observation.pmv` |
| `get_recent_history()` | `Memory` |
| `set_temperature()` | `Actuator` |

---

## Planner

Planner is independent from the LLM. It creates Goal, Strategy, and Constraints using Building State and History.

**Examples:**
- If Energy High → Increase Cooling Setpoint
- If Comfort Bad → Prioritize Comfort

---

## Memory

Stores every previous decision. Contains:

- State
- Decision

Provides `get_history()` so the LLM can inspect previous decisions.

---

## Safety Validator

Even if the LLM returns an unsafe value (e.g. 17°C), the Validator clamps it.

**Example:**
```
Allowed range: 20°C → 26°C
```

Final action is always safe.

---

## Logger

Stores into CSV:

- Observation
- Reward
- Decision
- Tool

Used later by Dashboard, Analytics, and Research.

---

## EnergyPlus Actuator

Receives:

```
Temperature → Setpoint → EnergyPlus Runtime API
```

Updates the simulation.

---

## Complete Communication Flow

```
EnergyPlus
  → Environment
  → Building State
  → Decision Engine
  → Planner
  → Memory
  → LLM Policy
  → LLM Client
  → Ollama
  → JSON
  → Decision Engine
  → MCP Server
  → Registry
  → EnergyPlus Tool
  → Result
  → Decision Engine
  → LLM
  → Final Action
  → Safety Validator
  → Environment
  → Actuator
  → EnergyPlus
  → Logger
  → Memory
```

---

## Current Agent Workflow

Current implementation follows this sequence:

```
Iteration 1 → read_pmv
Iteration 2 → read_energy
Iteration 3 → get_recent_history
Iteration 4 → Reason → final_action → set_temperature
```

---

## Responsibilities of Each File

| File | Responsibility |
|---|---|
| `runtime.py` | Starts simulation, registers callbacks, drives each timestep |
| `environment.py` | Converts raw EnergyPlus data into Building State |
| `sensors.py` | Reads EnergyPlus variables |
| `actuators.py` | Writes HVAC setpoints |
| `decision_engine.py` | Main autonomous agent loop |
| `planner.py` | Creates high-level strategy |
| `memory.py` | Stores previous states and decisions |
| `llm_policy.py` | Validates and interprets LLM responses |
| `llm_client.py` | Builds prompt and communicates with Ollama |
| `registry.py` | Stores available MCP tools |
| `server.py` | Executes requested MCP tools |
| `tools.py` | Implements sensor, memory, and actuator tools |
| `safety_validator.py` | Ensures safe temperature limits |
| `logger.py` | Logs simulation data to CSV |
| `reward.py` | Calculates reinforcement learning reward |

---

## Current Known Issue (for Debugging Context)

The overall architecture is functioning correctly:

- `tool_history` is correctly accumulated in the `DecisionEngine`.
- `tool_history` is correctly passed through `LLMPolicy` to `LLMClient`.
- The prompt correctly includes the `TOOLS EXECUTED SO FAR` section.
- Iteration 1 (`read_pmv`) and Iteration 2 (`read_energy`) complete successfully.
- The standalone Ollama connectivity test (`requests.post` with a simple prompt) succeeds immediately.

**The current unresolved issue is:**

> During Iteration 3, after printing `"🚀 Sending request to Ollama..."`, the request does not return.

This suggests the problem is most likely related to the **complexity or content of the Iteration 3 prompt** (or model inference on that prompt), rather than the Decision Engine, MCP infrastructure, or HTTP connectivity.
