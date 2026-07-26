from planner import Planner
from llm_policy import LLMPolicy
from memory import Memory
from safety_validator import SafetyValidator
from plan_executor import PlanExecutor


class AthenaAgent:

    def __init__(self):

        self.memory = Memory()

        self.planner = Planner()

        self.policy = LLMPolicy()

        self.validator = SafetyValidator()

        self.executor = PlanExecutor()

        self.step = 0

        self.planning_interval = 10

    def run(self, building_state):

        self.step += 1

        history = self.memory.get_history()

        # -----------------------------------
        # Replan
        # -----------------------------------

        if (
            self.executor.current_plan is None
            or self.step % self.planning_interval == 0
        ):

            print("\n🧠 Athena Planning...")

            plan = self.planner.create_plan(
                building_state,
                history
            )

            result = self.policy.decide(
                building_state,
                history,
                plan
            )

            action = result["temperature"]

            reasoning = result["reasoning"]

            confidence = result["confidence"]

            self.executor.update_plan(plan)

        else:

            print("\n⚡ Executing Cached Plan...")

            action = self.executor.execute(
                building_state
            )

            reasoning = "Executing cached plan."

            confidence = 1.0

            plan = self.executor.current_plan

        # -----------------------------------
        # Safety
        # -----------------------------------

        action = self.validator.validate(action)

        decision = {

            "temperature": action,

            "reasoning": reasoning,

            "confidence": confidence,

            "plan": plan

        }

        self.memory.add(
            building_state,
            decision
        )

        return decision