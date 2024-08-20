"""Approximation Algorithm Parameters Object"""

class ApxParams:

    """Approximation Algorithm Parameters Object"""

    def __init__(self,epsilon_r,epsilon_f,epsilon_b):
        self.update_parameters(epsilon_r,epsilon_f,epsilon_b)

    def update_parameters(self,epsilon_r,epsilon_f,epsilon_b):

        """Update \\epsilon_x parameters and dependent calculations"""

        self.epsilon_r = epsilon_r
        self.epsilon_f = epsilon_f
        self.epsilon_b = epsilon_b
        self.one_minus_epsilon = (1-self.epsilon_r)*(1-self.epsilon_b)*(1-self.epsilon_f)
        self.solution_multiplier = 1/self.one_minus_epsilon
        self.epsilon = 1-self.one_minus_epsilon

    def print_parameters(self):

        """ Print APX parameters"""

        print("APX Params")
        print("epsilon_r:",self.epsilon_r)
        print("epsilon_b:",self.epsilon_b)
        print("epsilon_f:",self.epsilon_f)
        print("(1-EPSILON):",self.one_minus_epsilon)
        print("EPSILON",self.epsilon)
