from sensors import BuildingSensors
from actuators import BuildingActuators
from state_builder import StateBuilder


class EnergyPlusEnvironment:

    def __init__(self, sensors, actuators, reward_function):

        self.sensors = sensors
        self.actuators = actuators
        self.reward_function = reward_function
        self.state_builder = StateBuilder()
        self.previous_observation = None
        self.previous_action = None

        self.initialized = False

    def initialize(self, state):

        if self.initialized:
            return

        print("Initializing Environment...")

        self.sensors.initialize(state)
        self.actuators.initialize(state)

        self.initialized = True

    def get_observation(self, state):

        return self.sensors.read(state)

    def get_reward(self, observation):

        return self.reward_function.calculate(
            observation
        )

    def apply_action(self, state, action):

        self.actuators.set_core_temperature(
            state,
            action
        )

    def store_transition(self, observation, action):
        self.previous_observation = observation
        self.previous_action = action

    def get_transition(self, observation):
        if self.previous_observation is None:
            return None

        reward = self.get_reward(observation)

        transition = {
            "state": self.previous_observation,
            "action": self.previous_action,
            "reward": reward,
            "next_state": observation
        }

        return transition

    def get_state(self, observation):
        # Bug 11 fix: was mis-indented causing return to be outside the method
        return self.state_builder.build(
            observation
        )