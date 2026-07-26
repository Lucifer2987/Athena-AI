class StateBuilder:

    def __init__(self):

        self.comfort_range = (-0.5, 0.5)

    def build(self, observation):

        temperature = observation["temperature"]
        pmv = observation["pmv"]
        electricity = observation["electricity"]

        # -----------------------
        # Comfort Status
        # -----------------------

        if pmv < -0.5:
            comfort_status = "Cold"

        elif pmv > 0.5:
            comfort_status = "Hot"

        else:
            comfort_status = "Comfortable"

        # -----------------------
        # Energy Status
        # -----------------------

        if electricity < 500_000:
            energy_status = "Low"

        elif electricity < 2_000_000:
            energy_status = "Medium"

        else:
            energy_status = "High"

        # -----------------------
        # State
        # -----------------------

        state = {

            "zone": "CORE_ZN",

            "temperature": round(
                temperature,
                2
            ),

            "pmv": round(
                pmv,
                2
            ),

            "comfort_status": comfort_status,

            "electricity": round(
                electricity,
                2
            ),

            "energy_status": energy_status,

            "goal": {

                "comfort": "Maintain PMV between -0.5 and 0.5",

                "energy": "Reduce electricity consumption"

            }

        }

        return state