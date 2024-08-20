"""Literature AVR task sets - canonical and KAVR"""

from avr_fxns import avr_task

class LitAvrTaskSets:

    """Literature AVR tak sets"""

    def __init__(self):

        kavr_18_can_w = [500, 1500, 2500, 3500, 4500, 5500, 6500]
        kavr_18_can_c = [0, 965, 576, 424, 343, 277, 246]
        kavr_18_can_a = 600000
        kavr_18_can_m = len(kavr_18_can_w)-1
        self.avr_task_instance_2018_existing = avr_task.AvrTask(
            kavr_18_can_m,kavr_18_can_w,kavr_18_can_c,kavr_18_can_a,"can")

        kavr_18_gen_w = [1200, 2200, 3200, 4200, 5200, 6200, 7200]
        kavr_18_gen_c = [0, 965, 576, 424, 343, 277, 246]
        kavr_18_gen_a = 600000
        kavr_18_gen_m = len(kavr_18_gen_w)-1
        self.avr_task_instance_2018_general = avr_task.AvrTask(
            kavr_18_gen_m,kavr_18_gen_w,kavr_18_gen_c,kavr_18_gen_a,"gen")
