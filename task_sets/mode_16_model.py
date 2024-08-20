"""Task Sets - Manually Defined 16-mode"""

#Includes
from avr_fxns import avr_task as AVR_TASK

class UserTaskSet:

    """35-mode task set"""

    def __init__(self):

        w_user_task_set = [0, 553, 4714, 5104, 6421, 6591,
        12693, 13966, 15938, 17092, 19378, 22569,
        24496, 31465, 35486, 38418, 46859]
        c_user_task_set = [0, 4776, 4584, 4308, 4041, 3422,
        3362, 3296, 3286, 2370, 2266, 1981,
        1504, 1408, 1264, 690, 656]
        a_user_task_set = 646276
        m_user_task_set = len(w_user_task_set)-1
        self.avr_task_instance_user_task_set = AVR_TASK.AvrTask(
            m_user_task_set,w_user_task_set,c_user_task_set,a_user_task_set,"m16")

# M: 16
# W: [0, 553, 4714, 5104, 6421, 6591, 12693, 13966, 15938, 17092, 19378, 22569, 24496, 31465, 35486, 38418, 46859]
# C: [0, 4776, 4584, 4308, 4041, 3422, 3362, 3296, 3286, 2370, 2266, 1981, 1504, 1408, 1264, 690, 656]
# A: 646276