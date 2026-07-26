"""
LLMClient  --  Athena AI  --  optimised for speed and reliability
- Single-shot prompt: building state always includes PMV + electricity + temperature,
  so we never need tool calls. The LLM is told to return final_action directly.
- Retry: up to 3 attempts with 30s per-chunk timeout before fallback.
- Robust JSON extraction: strips markdown fences if model adds them.
"""
import json
import re
import requests


class LLMClient:

    MODEL   = "qwen2.5:7b"
    URL     = "http://localhost:11434/api/generate"
    TIMEOUT = (8, 45)       # (connect_s, per-chunk-read_s) -- 45s for loaded Ollama
    RETRIES = 3

    def ask(self, building_state, history, plan, tool_history=None):
        """Send a single-shot request to Ollama and return parsed JSON dict."""

        prompt = self._build_prompt(building_state, history, plan)

        print("\n================ PROMPT SENT TO LLM ================")
        print(prompt)
        print("====================================================\n")

        last_error = None
        for attempt in range(1, self.RETRIES + 1):
            try:
                print(f"[SEND] Attempt {attempt}/{self.RETRIES} -> Ollama...")
                raw = self._stream_request(prompt)
                print("[OK] Response received from Ollama")
                print(f"\n========== RAW LLM OUTPUT ==========\n{raw}\n=====================================\n")
                return self._parse(raw)

            except TimeoutError as exc:
                last_error = exc
                print(f"[WARN] Attempt {attempt} timed out: {exc}")

            except Exception as exc:
                last_error = exc
                print(f"[WARN] Attempt {attempt} failed: {exc}")

        raise TimeoutError(
            f"Ollama did not respond after {self.RETRIES} attempts. "
            f"Last error: {last_error}"
        )

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------

    def _build_prompt(self, building_state, history, plan):
        """Return a compact, deterministic prompt.

        Design principles
        -----------------
        * The building state ALWAYS contains live PMV, electricity, and
          temperature from EnergyPlus sensors -- no tool calls required.
        * The LLM must return ONLY a JSON object with final_action.
        * Instructions fit in ~300 tokens so the full prompt stays under
          ~800 tokens even with history. This prevents model overload.
        """
        # Compact plan line
        strategy   = "; ".join(plan.get("strategy", [])) or "Maintain comfort and minimise energy"
        constraint = "; ".join(plan.get("constraints", [])) or "PMV in [-0.5, 0.5]; T in [20, 26] C"

        # Last 3 history entries summarised to key fields only
        hist_rows = []
        for h in history[-3:]:
            hist_rows.append({
                "temp_C":  round(float(h.get("temperature", 22)), 2),
                "pmv":     round(float(h.get("pmv", 0)),          2),
                "elec_W":  round(float(h.get("electricity", 0)),  0),
                "action":  h.get("action", 22),
            })

        # Core state -- only what the LLM actually needs
        state_summary = {
            "zone":        building_state.get("zone", "CORE_ZN"),
            "temp_C":      round(float(building_state.get("temperature", 22)), 2),
            "pmv":         round(float(building_state.get("pmv", 0)),         2),
            "elec_W":      round(float(building_state.get("electricity", 0)), 0),
            "comfort":     building_state.get("comfort_status", "Unknown"),
            "energy_load": building_state.get("energy_status",  "Unknown"),
        }

        prompt = (
            "You are Athena AI, an autonomous HVAC controller.\n\n"
            f"LIVE STATE: {json.dumps(state_summary)}\n\n"
            f"HISTORY (last {len(hist_rows)} steps): {json.dumps(hist_rows)}\n\n"
            f"STRATEGY: {strategy}\n"
            f"CONSTRAINTS: {constraint}\n\n"
            "TASK: Choose the optimal temperature setpoint for CORE_ZN HVAC.\n"
            "- Keep PMV between -0.5 and 0.5 (comfort band).\n"
            "- Minimise electricity demand where possible.\n"
            "- Do NOT cool below 20 C or heat above 26 C.\n\n"
            "Return ONLY valid JSON -- no markdown, no extra text:\n"
            '{"reasoning":"<one sentence>","confidence":<0.80-0.99>,'
            '"final_action":{"tool":"set_temperature","arguments":{"temperature":<float 20-26>}}}'
        )

        return prompt

    # ------------------------------------------------------------------
    # HTTP streaming
    # ------------------------------------------------------------------

    def _stream_request(self, prompt: str) -> str:
        payload = {
            "model":   self.MODEL,
            "prompt":  prompt,
            "stream":  True,
            "options": {
                "temperature":  0.05,   # near-zero temp -> deterministic JSON
                "num_predict":  120,    # JSON answer is ~80 tokens
                "top_p":        0.9,
                "repeat_penalty": 1.1,
            },
        }

        chunks = []
        try:
            with requests.post(
                self.URL,
                json=payload,
                stream=True,
                timeout=self.TIMEOUT,
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    obj   = json.loads(line)
                    token = obj.get("response", "")
                    chunks.append(token)
                    if obj.get("done", False):
                        break

        except requests.exceptions.Timeout as exc:
            raise TimeoutError(str(exc)) from exc

        return "".join(chunks).strip()

    # ------------------------------------------------------------------
    # JSON parsing  --  robust against markdown fences
    # ------------------------------------------------------------------

    def _parse(self, raw: str) -> dict:
        # Strip ```json ... ``` fences if model adds them
        clean = re.sub(r"```[a-z]*\s*", "", raw).strip()

        # Direct parse
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            pass

        # Extract first {...} block
        m = re.search(r"\{[\s\S]*\}", clean)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                pass

        raise ValueError(f"Could not parse JSON from LLM output:\n{raw}")