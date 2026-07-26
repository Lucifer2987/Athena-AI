import sys
import io
import shutil
from datetime import datetime
from pathlib import Path

# Force UTF-8 output so prints work on Windows cp1252 terminals
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ------------------------------------------------------------------
# STEP 1: Load config first (provides ENERGYPLUS_DIR, EXAMPLE_FILE, etc.)
# STEP 2: Insert EnergyPlus into sys.path BEFORE any local imports that
#         may transitively import pyenergyplus at module level.
# ------------------------------------------------------------------
from config import ENERGYPLUS_DIR, EXAMPLE_FILE, WEATHER_FILE, OUTPUT_DIR, PLANNING_INTERVAL

sys.path.insert(0, str(ENERGYPLUS_DIR))
sys.path.insert(0, str(ENERGYPLUS_DIR / "pyenergyplus"))

# ------------------------------------------------------------------
# STEP 3: Import pyenergyplus (now on path)
# ------------------------------------------------------------------
from pyenergyplus.api import EnergyPlusAPI

# ------------------------------------------------------------------
# STEP 4: Import local Athena modules (may use pyenergyplus internally)
# ------------------------------------------------------------------
from sensors import BuildingSensors
from actuators import BuildingActuators
from environment import EnergyPlusEnvironment
from reward import RewardFunction
from decision_engine import DecisionEngine
from logger import SimulationLogger

from mcp.registry import MCPRegistry
from mcp.tools import EnergyPlusTools


# ==================================================
# Delivery Requirement 2: Save baseline IDF copy
# ==================================================

def _save_building_artifacts():
    """Copy the baseline IDF and write a modified-building notes file."""
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Baseline IDF copy
    baseline_dest = logs_dir / "baseline_building.idf"
    try:
        shutil.copy(EXAMPLE_FILE, baseline_dest)
        print(f"[RUNTIME] Baseline IDF saved -> {baseline_dest}")
    except Exception as exc:
        print(f"[RUNTIME] Could not save baseline IDF: {exc}")

    # Modified building notes
    notes_path = logs_dir / "modified_building_notes.txt"
    notes = (
        "Athena AI -- Runtime Modification Notes\n"
        "=========================================\n"
        f"Run timestamp : {datetime.now().isoformat()}\n"
        f"Baseline IDF  : {EXAMPLE_FILE}\n"
        f"Weather file  : {WEATHER_FILE}\n"
        f"Output dir    : {OUTPUT_DIR}\n"
        "\nModifications applied at runtime (via EnergyPlus Python API):\n"
        "  - Zone HVAC setpoint actuator: 'CORE_ZN ZN PSZ-AC-1'\n"
        "    Variable: 'System Node Setpoint Temp'\n"
        "    Control : Athena AI autonomous LLM agent (Qwen2.5 via Ollama)\n"
        "  - Setpoint range enforced: 20.0 C - 26.0 C (SafetyValidator)\n"
        "  - Planning interval: every 10 timesteps\n"
        "  - MCP tools used: read_pmv, read_energy, read_temperature,\n"
        "                    get_recent_history, set_temperature\n"
        "\nNote: The .idf file itself is NOT modified; all changes are applied\n"
        "dynamically through the EnergyPlus Runtime API actuator interface.\n"
    )
    notes_path.write_text(notes, encoding="utf-8")
    print(f"[RUNTIME] Modified building notes saved -> {notes_path}")


_save_building_artifacts()


# ==================================================
# Initialize API and components
# ==================================================

api             = EnergyPlusAPI()
sensors         = BuildingSensors(api)
actuators       = BuildingActuators(api)
reward_function = RewardFunction()
logger          = SimulationLogger(rotate=True)   # Archives previous CSV on restart

env             = EnergyPlusEnvironment(sensors, actuators, reward_function)
registry        = MCPRegistry()
decision_engine = DecisionEngine(registry)

tools = EnergyPlusTools(
    sensors,
    actuators,
    decision_engine.memory,
)

state = api.state_manager.new_state()


# ==================================================
# Callback: called once per environment setup
# ==================================================

def begin_environment(state_argument):
    print("\n[ATHENA] Simulation Started\n")
    env.initialize(state_argument)

    print("\n========== SENSOR HANDLES ==========")
    print(sensors.handles)

    print("\n========== ACTUATOR HANDLES ==========")
    print(actuators.handles)

    # Register MCP tools (safe to call multiple times -- registry handles duplicates)
    registry.register("read_temperature",   tools.read_temperature,   "Read current zone temperature")
    registry.register("read_energy",        tools.read_energy,        "Read building electricity")
    registry.register("read_pmv",           tools.read_pmv,           "Read current PMV")
    registry.register("get_recent_history", tools.get_recent_history, "Retrieve recent decision history")
    registry.register("set_temperature",    tools.set_temperature,    "Apply HVAC temperature setpoint")

    print("\n========== MCP TOOLS ==========")
    for name, description in registry.list_tools().items():
        print(f"  {name} -> {description}")


# ==================================================
# Callback: main control loop (every system timestep)
# ==================================================

def control_loop(state_argument):

    # ---- Observation ----
    observation = env.get_observation(state_argument)
    if observation is None:
        return

    building_state = env.get_state(observation)
    print("\n========== BUILDING STATE ==========")
    print(building_state)

    # ---- Transition (previous step) ----
    transition = env.get_transition(observation)
    if transition is not None:
        print("\n========== TRANSITION ==========")
        print(transition)

    # ---- Decision ----
    decision = decision_engine.decide(building_state)
    action   = decision["temperature"]

    # ---- Reward ----
    reward = env.get_reward(observation)

    print("\n========== OBSERVATION ==========")
    print(observation)

    print("\n========== REWARD ==========")
    print(reward)

    print("\n========== ATHENA AI ==========")
    print(f"Reasoning : {decision['reasoning']}")
    print(f"Confidence: {decision['confidence']}")
    print(f"Action    : {action} C")

    if "plan" in decision:
        print("\n========== PLAN ==========")
        print(decision["plan"])

    # ---- Log (tool column never N/A) ----
    tools_used = ", ".join(t["tool"] for t in decision.get("tool_history", []))
    if not tools_used:
        tools_used = "set_temperature"

    logger.log(observation, reward, decision, tool=tools_used)

    # ---- Apply setpoint ----
    env.apply_action(state_argument, action)

    # ---- Store transition for next step ----
    env.store_transition(observation, action)


# ==================================================
# Register EnergyPlus callbacks
# ==================================================

api.runtime.callback_begin_new_environment(
    state, begin_environment
)
api.runtime.callback_begin_system_timestep_before_predictor(
    state, control_loop
)


# ==================================================
# Run EnergyPlus simulation
# ==================================================

args = [
    "-w", str(WEATHER_FILE),
    "-d", str(OUTPUT_DIR),
    str(EXAMPLE_FILE),
]

api.runtime.run_energyplus(state, args)

print("\n[ATHENA] Simulation Finished Successfully")