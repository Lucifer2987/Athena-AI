class EnergyPlusTools:

    def __init__(self, sensors, actuators, memory):

        self.sensors = sensors
        self.actuators = actuators
        self.memory = memory

    # ==========================================
    # Sensor Tools
    # ==========================================

    def read_temperature(self, context):

        observation = context["observation"]

        return observation["temperature"]

    def read_energy(self, context):

        observation = context["observation"]

        return observation["electricity"]

    def read_pmv(self, context):

        observation = context["observation"]

        return observation["pmv"]

    # ==========================================
    # Memory Tool
    # ==========================================

    def get_recent_history(self, context):

        return self.memory.get_history()

    # ==========================================
    # Actuator Tool
    # ==========================================

    def set_temperature(
        self,
        context,
        temperature
    ):

        return {

            "action": "set_temperature",

            "value": temperature

        }