class PlanExecutor:

    def __init__(self):

        self.current_plan = None

    def update_plan(self, plan):

        self.current_plan = plan

    def execute(self, building_state):

        if self.current_plan is None:

            return 22.0

        strategy = self.current_plan.get("strategy", [])

        if any("Increase cooling" in s for s in strategy):

            return min(
                building_state["temperature"] + 0.2,
                26
            )

        if any("Maintain current" in s for s in strategy):

            return building_state["temperature"]

        if any("Prioritize restoring" in s for s in strategy):

            return 22.0

        return 22.0