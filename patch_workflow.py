from pathlib import Path

target = Path('dashboard/components.py')
src = target.read_text(encoding='utf-8')

idx = src.find('def render_agent_workflow')
end = src.find('\ndef render_decision_panel', idx)

NEW = """def render_agent_workflow(latest_row_dict: dict) -> None:
    stages = [
        ("Observe Environment",  "Sensors capture Temp, PMV and Electricity from EnergyPlus API"),
        ("Read PMV",             "MCP execute read_pmv -- comfort index acquired"),
        ("Read Energy",          "MCP execute read_energy -- electricity demand acquired"),
        ("Consult Memory",       "Retrieve historical trajectory from memory buffer"),
        ("LLM Policy Reasoning", "Qwen2.5 generates candidate HVAC setpoint"),
        ("Safety Validation",    "SafetyValidator enforces 20C - 26C boundaries"),
        ("Apply Temperature",    "Actuator writes setpoint to EnergyPlus System Node"),
    ]

    # ------------------------------------------------------------------
    # Derive stage completion from CSV row data, NOT just the tool name.
    # The new adaptive prompt often skips tool calls and goes straight to
    # final_action -- so tool = "read_pmv" doesn't mean only PMV was done.
    # Instead we infer each stage from what was actually recorded in the row.
    # ------------------------------------------------------------------
    row = latest_row_dict

    def _is_real(val):
        if val is None:
            return False
        try:
            import math
            return not math.isnan(float(val))
        except Exception:
            return bool(val)

    has_pmv         = _is_real(row.get("pmv")) or _is_real(row.get("temperature"))
    has_electricity = _is_real(row.get("electricity"))
    reasoning_text  = _safe_text(row.get("reasoning"))
    is_fallback     = "Fallback action" in reasoning_text or not reasoning_text
    has_reasoning   = not is_fallback
    conf_val        = row.get("confidence")
    has_confidence  = _is_real(conf_val) and float(conf_val or 0) > 0
    has_action      = _is_real(row.get("action"))

    completed = [
        True,                                # 0: Observe       -- always done
        has_pmv,                             # 1: Read PMV      -- temp/pmv in row
        has_electricity,                     # 2: Read Energy   -- electricity in row
        has_reasoning or has_confidence,     # 3: Consult Memory
        has_reasoning,                       # 4: LLM Reason
        has_confidence,                      # 5: Safety Valid  -- confidence > 0
        has_action,                          # 6: Apply Temp    -- action written
    ]

    # Active = first incomplete stage; if all done, highlight the last one
    current_index = next((i for i, done in enumerate(completed) if not done), 6)

    st.markdown(
        '''
<div class="glass-card animate-in">
  <div class="section-label">Agent Execution Cycle</div>
  <h3 style="font-size:1.25rem;font-weight:800;margin:0.3rem 0 0.8rem;color:var(--text-main);">Athena Agent Decision Pipeline</h3>
  <div class="workflow-pipeline">
''',
        unsafe_allow_html=True,
    )

    for index, (name, desc) in enumerate(stages):
        if completed[index] and index < current_index:
            cls, status, status_txt = "completed", "done", "DONE"
        elif index == current_index and completed[index]:
            cls, status, status_txt = "active", "active", "ACTIVE"
        elif index == current_index:
            cls, status, status_txt = "active", "active", "RUNNING"
        else:
            cls, status, status_txt = "", "pending", "QUEUED"

        node_html = f'''
    <div class="workflow-node {cls}">
      <div class="node-number">{index + 1}</div>
      <div>
        <div class="node-title">{name}</div>
        <div class="node-desc">{desc}</div>
      </div>
      <div class="node-status-badge {status}">{status_txt}</div>
    </div>
'''
        st.markdown(node_html, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)
"""

new_src = src[:idx] + NEW + src[end:]
target.write_text(new_src, encoding='utf-8')
print("PATCHED OK")
print(f"Old block = {end - idx} chars, New block = {len(NEW)} chars")
