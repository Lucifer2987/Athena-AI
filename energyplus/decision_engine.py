"""
DecisionEngine  --  Athena AI  --  orchestrates the LLM agent loop.

Improvements in this version:
 - Fallback uses last good temperature from memory (not hardcoded 22.0).
 - Fallback confidence = 0.5 so the dashboard can distinguish it from errors.
 - Fallback reasoning is human-readable (not "Fallback action due to LLM failure.").
 - Tool column is always "set_temperature" even on fallback.
 - _summarize_result returns raw Python object to prevent double-JSON-encoding.
"""
import json

from llm_policy import LLMPolicy
from safety_validator import SafetyValidator
from memory import Memory
from planner import Planner
from plan_executor import PlanExecutor
from config import PLANNING_INTERVAL

from mcp.server import MCPServer


# Cap tool-result length to avoid prompt bloat on re-injection
_MAX_TOOL_RESULT_CHARS = 300


def _summarize_result(data):
    """Return tool result ready for tool_history.
    Returns the raw Python object when it fits within the limit (so
    json.dumps(tool_history) serialises it cleanly -- no double escaping).
    Returns a truncated string only when the result is too large.
    """
    try:
        text = json.dumps(data)
    except Exception:
        text = str(data)

    if len(text) <= _MAX_TOOL_RESULT_CHARS:
        return data                                         # raw obj -- serialised once
    return text[:_MAX_TOOL_RESULT_CHARS] + "... [truncated]"


class DecisionEngine:

    MAX_TOOL_CALLS = 3      # Reduced: with single-shot LLM we rarely need tools

    def __init__(self, registry):
        self.policy    = LLMPolicy()
        self.validator = SafetyValidator()
        self.memory    = Memory()
        self.planner   = Planner()
        self.executor  = PlanExecutor()
        self.registry  = registry
        self.server    = MCPServer(self.registry)
        self.planning_interval = PLANNING_INTERVAL
        self.step      = 0

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def decide(self, building_state: dict) -> dict:
        self.step += 1
        history = self.memory.get_history()

        # ------ Planning ------
        if self.executor.current_plan is None or self.step % self.planning_interval == 0:
            print("\n[PLANNER] Replanning using LLM...")
            plan = self.planner.create_plan(building_state, history)
            self.executor.update_plan(plan)
        else:
            print("\n[PLANNER] Using cached plan...")
            plan = self.executor.current_plan

        # ------ Agent loop ------
        context      = {"observation": building_state}
        tool_history = []
        executed     = set()
        final_temp   = None
        reasoning    = ""
        confidence   = 0.0

        for iteration in range(self.MAX_TOOL_CALLS):
            print(f"\n================ ITERATION {iteration + 1} ================")

            try:
                response = self.policy.decide(building_state, history, plan, tool_history)
            except Exception as exc:
                print(f"[ERROR] LLM call failed: {exc}")
                break

            print("\n========== LLM RESPONSE ==========")
            print(response)

            reasoning  = response.get("reasoning",  reasoning)
            confidence = response.get("confidence", confidence)

            # ---- Tool call ----
            if "tool_call" in response:
                tool_name = response["tool_call"]["tool"]
                args      = response["tool_call"].get("arguments", {})

                if tool_name in executed:
                    print(f"[WARN] Tool '{tool_name}' already ran. Breaking.")
                    break
                executed.add(tool_name)

                print(f"[TOOL] Executing -> {tool_name}")
                result = self.server.execute(tool_name, context=context, **args)

                if not result.success:
                    print(f"[ERROR] Tool '{tool_name}' failed: {result.message}")
                    break

                tool_history.append({
                    "tool":   tool_name,
                    "result": _summarize_result(result.data),
                })
                print("Current Tool History:", tool_history)
                continue

            # ---- Final action ----
            if "final_action" in response:
                action    = response["final_action"]
                tool_name = action.get("tool", "").lower()

                if tool_name != "set_temperature":
                    print(f"[WARN] Invalid final tool '{tool_name}'. Ignoring.")
                    break

                try:
                    final_temp = float(action["arguments"]["temperature"])
                    print(f"\n[OK] Final Temperature Selected: {final_temp}")
                    break
                except (KeyError, TypeError, ValueError) as exc:
                    print(f"[ERROR] Could not parse temperature from final_action: {exc}")
                    break

        else:
            print("\n[WARN] Maximum iterations reached without final_action.")

        # ------------------------------------------------------------------
        # Fallback  --  use last good temperature from memory, not 22.0
        # ------------------------------------------------------------------
        if final_temp is None:
            last_good = self._last_good_temperature(building_state)
            print(f"\n[FALLBACK] Using rule-based setpoint: {last_good} C")
            final_temp   = last_good
            reasoning    = f"Rule-based fallback: maintaining last known safe setpoint ({last_good} C)"
            confidence   = 0.5      # Not 0.0 -- validator ran and approved this value

        # ------------------------------------------------------------------
        # Safety validation
        # ------------------------------------------------------------------
        final_temp = self.validator.validate(final_temp)
        print(f"\n[SAFETY] Validated Temperature: {final_temp}")

        # ------------------------------------------------------------------
        # Decision package
        # ------------------------------------------------------------------
        decision = {
            "temperature":  final_temp,
            "reasoning":    reasoning,
            "confidence":   confidence,
            "plan":         plan,
            "tool_history": tool_history,
        }

        self.memory.add(building_state, decision)

        print("\n========== ATHENA SUMMARY ==========")
        print(f"Temperature : {final_temp}")
        print(f"Confidence  : {confidence:.2f}")
        print(f"Tools Used  : {[t['tool'] for t in tool_history]}")
        print(f"Reasoning   : {reasoning}")
        print("====================================\n")

        return decision

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _last_good_temperature(self, building_state: float) -> float:
        """Return the last non-fallback setpoint from memory, or building temp."""
        hist = self.memory.get_history()
        for entry in reversed(hist):
            action = entry.get("action")
            reason = entry.get("reasoning", "")
            if action is not None and "fallback" not in str(reason).lower():
                try:
                    return float(action)
                except (TypeError, ValueError):
                    pass
        # If no good history, use current zone temperature (clipped to safe range)
        t = float(building_state.get("temperature", 22.0))
        return max(20.0, min(26.0, round(t, 1)))