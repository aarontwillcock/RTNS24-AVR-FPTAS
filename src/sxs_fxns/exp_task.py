"""Experiment task class"""

import copy

class ExperimentTask:

    """Experiment task format"""

    def __init__(self, algorithm,
        algorithm_params, avr_task_instance, delta_set,
        print_config):

        self.algorithm = copy.deepcopy(algorithm)
        self.algorithm_params = copy.deepcopy(algorithm_params)
        self.avr_task_instance = copy.deepcopy(avr_task_instance)
        self.delta_set = copy.deepcopy(delta_set)
        self.print_config = copy.deepcopy(print_config)
