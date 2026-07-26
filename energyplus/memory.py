from collections import deque


class Memory:

    def __init__(self, max_history=10):
        # Increased from 5 -> 10 so we retain more context across timesteps
        self.history = deque(maxlen=max_history)

    def add(self, building_state, decision):

        self.history.append({

            "temperature": building_state["temperature"],

            "pmv": building_state["pmv"],

            "electricity": building_state["electricity"],

            "comfort_status": building_state["comfort_status"],

            "energy_status": building_state["energy_status"],

            "action": decision["temperature"]

        })

    def get_history(self):
        """Return the full history list."""
        return list(self.history)

    def get_recent(self, n=3):
        """Return the last n entries only.
        Use this when injecting history into the LLM prompt to avoid bloat.
        """
        history = list(self.history)
        return history[-n:] if len(history) >= n else history

    def clear(self):

        self.history.clear()