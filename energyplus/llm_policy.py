"""
LLMPolicy  --  thin adapter between DecisionEngine and LLMClient.

Design: re-raises exceptions so DecisionEngine.decide() can apply its own
intelligent fallback (last good temperature from memory, confidence 0.5,
human-readable reasoning). LLMPolicy must NOT swallow errors here.
"""
from llm_client import LLMClient


class LLMPolicy:

    def __init__(self):
        self.client = LLMClient()

    def decide(self, building_state, history, plan, tool_history=None):
        """Call the LLM and return a structured response dict.

        Returns one of:
          {"reasoning": ..., "confidence": ..., "tool_call":    {...}}
          {"reasoning": ..., "confidence": ..., "final_action": {...}}

        Raises:
          Any exception from LLMClient -- deliberately re-raised so that
          DecisionEngine.decide() can run its own intelligent fallback.
        """
        if tool_history is None:
            tool_history = []

        # Will raise TimeoutError / ValueError / requests errors on failure.
        # DO NOT catch here -- let DecisionEngine handle it with smart fallback.
        result = self.client.ask(
            building_state=building_state,
            history=history,
            plan=plan,
            tool_history=tool_history,
        )

        reasoning  = result.get("reasoning",  "No reasoning provided.")
        confidence = float(result.get("confidence", 0.0))

        if "tool_call" in result:
            return {
                "reasoning":  reasoning,
                "confidence": confidence,
                "tool_call":  result["tool_call"],
            }

        if "final_action" in result:
            return {
                "reasoning":    reasoning,
                "confidence":   confidence,
                "final_action": result["final_action"],
            }

        raise RuntimeError(
            f"LLM returned neither tool_call nor final_action. "
            f"Raw result keys: {list(result.keys())}"
        )