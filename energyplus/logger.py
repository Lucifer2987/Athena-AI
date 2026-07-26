"""
SimulationLogger  --  Athena AI
- Writes UTF-8 safe CSV (strips non-ASCII from text fields).
- Rotates the log file at the start of each new simulation run.
- Never logs N/A for the tool column: defaults to "set_temperature".
- Step counter is global across restarts (reads last step from file).
"""
import csv
import os
import re
import shutil
from datetime import datetime
from pathlib import Path


LOG_DIR  = Path("logs")
LOG_FILE = LOG_DIR / "simulation_log.csv"
HEADER   = ["step", "temperature", "pmv", "electricity",
             "reward", "action", "tool", "reasoning", "confidence"]


def _ascii_safe(text: str) -> str:
    """Remove non-ASCII characters that break CSV readers."""
    # Replace degree sign and common symbols explicitly
    text = str(text)
    text = text.replace("\u00b0", " deg").replace("\u2019", "'")
    # Strip anything else above ASCII 127
    return re.sub(r"[^\x00-\x7F]", "", text)


class SimulationLogger:

    def __init__(self, rotate: bool = True):
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        if rotate and LOG_FILE.exists():
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive = LOG_DIR / f"simulation_log_{ts}.csv"
            shutil.copy(LOG_FILE, archive)
            print(f"[LOGGER] Archived previous log to {archive}")

        # Always create a fresh file for this run
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(HEADER)

        # Step counter
        self.step = 0

    def log(self, observation: dict, reward: float, decision: dict, tool: str = "set_temperature") -> None:
        """Append one row to the CSV log."""
        self.step += 1

        # Tool must never be empty / N/A
        if not tool or tool.strip().upper() in ("N/A", "", "NONE"):
            tool = "set_temperature"

        reasoning = _ascii_safe(decision.get("reasoning", ""))
        confidence = decision.get("confidence", 0.0)

        row = [
            self.step,
            round(float(observation.get("temperature", 0)), 4),
            round(float(observation.get("pmv", 0)),         4),
            round(float(observation.get("electricity", 0)), 4),
            round(float(reward),                            6),
            round(float(decision.get("temperature", 22)),  2),
            tool,
            reasoning,
            round(float(confidence), 4),
        ]

        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(row)