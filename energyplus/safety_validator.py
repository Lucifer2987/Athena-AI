class SafetyValidator:

    def __init__(self):

        self.minimum_temperature = 20.0
        self.maximum_temperature = 26.0
        self.default_temperature = 22.0

    def validate(self, action):

        if action is None:
            return self.default_temperature

        try:
            action = float(action)
        except Exception:
            return self.default_temperature

        if action < self.minimum_temperature:
            action = self.minimum_temperature

        if action > self.maximum_temperature:
            action = self.maximum_temperature

        return round(action, 1)