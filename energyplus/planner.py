class Planner:

    def __init__(self):
        pass

    def create_plan(self, building_state, history):

        plan = {

            "goal": "Maintain occupant comfort while minimizing HVAC energy consumption.",

            "strategy": [],

            "constraints": [

                "PMV must remain between -0.5 and 0.5",

                "Temperature must remain between 20 deg C and 26 deg C"

            ]

        }

        # --------------------------
        # Comfort Strategy
        # --------------------------

        if building_state["comfort_status"] != "Comfortable":

            plan["strategy"].append(

                "Prioritize restoring occupant comfort."

            )

        # --------------------------
        # Energy Strategy
        # --------------------------

        if building_state["energy_status"] == "High":

            plan["strategy"].append(

                "Increase cooling setpoint gradually to reduce HVAC energy."

            )

        elif building_state["energy_status"] == "Medium":

            plan["strategy"].append(

                "Optimize cooling while maintaining comfort."

            )

        else:

            plan["strategy"].append(

                "Maintain current operating conditions."

            )

        # --------------------------
        # History Awareness
        # --------------------------

        if len(history) >= 3:

            energies = [

                h["electricity"]

                for h in history[-3:]

            ]

            if energies[2] > energies[1] > energies[0]:

                plan["strategy"].append(

                    "Electricity has increased for three consecutive timesteps."

                )

        return plan