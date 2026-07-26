class BuildingSensors:

    def __init__(self, api):

        self.api = api

        self.handles = {}

        self.initialized = False

    def initialize(self, state):

        print("Initializing Sensors...")

        self.handles["temperature"] = self.api.exchange.get_variable_handle(
            state,
            "Zone Mean Air Temperature",
            "CORE_ZN"
        )

        self.handles["electricity"] = self.api.exchange.get_variable_handle(
            state,
            "Facility Total Purchased Electricity Energy",
            "WHOLE BUILDING"
        )

        self.handles["pmv"] = self.api.exchange.get_variable_handle(
            state,
            "Zone Thermal Comfort Fanger Model PMV",
            "CORE_ZN PEOPLE"
        )

        print("Sensor Handles:")
        print(self.handles)

        # Bug 10 fix: only mark initialized if ALL handles are valid
        all_ok = True
        for name, handle in self.handles.items():

            if handle == -1:

                print(f"[FAIL] Failed to get handle for '{name}'")
                all_ok = False

            else:

                print(f"[OK] {name} handle = {handle}")

        if all_ok:
            self.initialized = True
        else:
            print(
                "[WARN] One or more sensor handles are invalid. "
                "Sensor reads will be skipped until handles are valid."
            )

    def read(self, state):

        # Wait until initialize() has completed with all valid handles
        if not self.initialized:
            return None

        # Safety check
        required = ["temperature", "electricity", "pmv"]

        for sensor in required:

            if sensor not in self.handles:

                print(f"[WARN] Missing sensor handle: {sensor}")

                return None

        return {

            "temperature": self.api.exchange.get_variable_value(
                state,
                self.handles["temperature"]
            ),

            "electricity": self.api.exchange.get_variable_value(
                state,
                self.handles["electricity"]
            ),

            "pmv": self.api.exchange.get_variable_value(
                state,
                self.handles["pmv"]
            )
        }