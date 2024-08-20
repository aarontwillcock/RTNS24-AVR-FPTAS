"""SXS Task and related classes"""

import copy

class SxsTask:

    """Side by side runner task format"""

    def __init__(self, avr_task_instance,
        apx_obj_instance, delta_set, method_set,
        kavr_config, print_config):

        self.avr_task_instance = copy.deepcopy(avr_task_instance)
        self.apx_obj_instance = copy.deepcopy(apx_obj_instance)
        self.delta_set = copy.deepcopy(delta_set)
        self.method_set = copy.deepcopy(method_set)
        self.kavr_config = copy.deepcopy(kavr_config)
        self.print_config = copy.deepcopy(print_config)
