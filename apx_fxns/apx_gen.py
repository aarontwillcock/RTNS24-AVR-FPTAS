"""Module for generating APX algorithm parameters"""

import random
import copy
from . import apx_obj as APX_OBJ

class AvrApxGen:

    """Class for generating APX algorithm parameters"""

    def __init__(self,
        delta_b,epsilon_repeating_b, epsilon_beta_b,
        epsilon_final_b, one_minus_epsilon):

        self.delta_b = copy.deepcopy(delta_b)
        self.epsilon_repeating_b = copy.deepcopy(epsilon_repeating_b)
        self.epsilon_beta_b = copy.deepcopy(epsilon_beta_b)
        self.epsilon_final_b = copy.deepcopy(epsilon_final_b)
        self.one_minus_epsilon = copy.deepcopy(one_minus_epsilon)

    def generate_apx_obj(self):

        """Create APX object with parameters"""

        #Default to out of spec
        out_of_specification = True

        #Continue trying until in spec
        while out_of_specification:

            #Approximation Parameter
            #   DELTA
            # delta = random.randint(self.delta_b[0], self.delta_b[1])
            #   Speeds (rpm)
            epsilon_repeating = random.randint(
                self.epsilon_repeating_b[0],
                self.epsilon_repeating_b[1])
            epsilon_repeating = epsilon_repeating/100
            #   WCET (ms)
            epsilon_beta = random.randint(self.epsilon_beta_b[0], self.epsilon_beta_b[1])
            epsilon_beta = epsilon_beta/100
            #   Final
            epsilon_final = random.randint(self.epsilon_final_b[0], self.epsilon_final_b[1])
            epsilon_final = epsilon_final/100
            #   Acceleration
            one_minus_epsilon = (1-epsilon_repeating)*(1-epsilon_beta)

            #Test for in spec
            if (one_minus_epsilon >= self.one_minus_epsilon[0]/100 and
                    one_minus_epsilon <= self.one_minus_epsilon[1]/100):

                out_of_specification = False


        #Create AVR Task
        avr_apx_instance = APX_OBJ.ApxObj(epsilon_repeating,epsilon_beta,epsilon_final)

        #Return Task
        return avr_apx_instance
