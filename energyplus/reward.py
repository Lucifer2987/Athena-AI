class RewardFunction:

    def _compute(self, observation):

        pmv = observation["pmv"]
        electricity = observation["electricity"]

        comfort_reward = max(0, 1 - abs(pmv))
        energy_penalty = electricity / 10_000_000
        reward = comfort_reward - energy_penalty

        return reward, comfort_reward, energy_penalty


    def calculate(self, observation):

        reward, _, _ = self._compute(observation)

        return reward


    def explain(self, observation):

        reward, comfort_reward, energy_penalty = self._compute(observation)

        return {
            "reward": reward,
            "comfort_reward": comfort_reward,
            "energy_penalty": energy_penalty
        }