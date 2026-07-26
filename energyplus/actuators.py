class BuildingActuators:

    def __init__(self, api):

        self.api = api
        self.handles = {}

    def initialize(self, state):

        print("Initializing Actuators...")

        self.handles["core_temp"] = self.api.exchange.get_actuator_handle(
            state,
            "System Node Setpoint",
            "Temperature Setpoint",
            "CORE_ZN AIR NODE"
        )

        print(self.handles)

        # Bug 9 fix: warn if the actuator handle is invalid
        if self.handles["core_temp"] == -1:
            print(
                "[FAIL] Failed to get actuator handle for 'core_temp'. "
                "Temperature setpoints will NOT be applied."
            )
        else:
            print(f"[OK] core_temp actuator handle = {self.handles['core_temp']}")

    def set_core_temperature(self, state, temperature):

        # Bug 9 fix: guard against invalid (-1) handle before writing
        handle = self.handles.get("core_temp", -1)

        if handle == -1:
            print(
                f"[WARN] Actuator handle invalid. "
                f"Cannot apply temperature setpoint: {temperature}"
            )
            return

        self.api.exchange.set_actuator_value(
            state,
            handle,
            temperature
        )