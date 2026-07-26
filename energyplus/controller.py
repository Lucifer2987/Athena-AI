class RuleBasedController:

    def decide(self, building_state):

        pmv = building_state["pmv"]

        if pmv < -0.5:
            return 24.0

        elif pmv > 0.5:
            return 21.0

        else:
            return 22.0