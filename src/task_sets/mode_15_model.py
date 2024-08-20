"""Task Sets - Manually Defined 15-mode"""

#Includes
from .experiment_helper_functions import avr_task as AVR_TASK

class UserTaskSet:

    """35-mode task set"""

    def __init__(self):

        w_user_task_set = [0, 646, 1068, 1472,
        1842, 4879, 5515, 5685, 5782, 7220, 7433, 9172,
        9207, 9236, 9676, 9992]
        c_user_task_set = [0, 987, 974, 972,
        949, 856, 779, 715, 607, 483, 436, 422,
        234, 215, 124, 116]
        a_user_task_set = 248012
        m_user_task_set = len(w_user_task_set)-1
        self.avr_task_instance_user_task_set = AVR_TASK.AvrTask(
            m_user_task_set,w_user_task_set,c_user_task_set,a_user_task_set)


#Based on:
# 744368,-1,58.94321770000005,96.78354480000002,1.9295649000000026,744368,0,744368,1,15,"[0, 646, 1068, 1472, 1842, 4879, 5515, 5685, 5782, 7220, 7433, 9172, 9207, 9236, 9676, 9992]","[0, 987, 974, 972, 949, 856, 779, 715, 607, 483, 436, 422, 234, 215, 124, 116]",248012,0.2,0.1,0.69,0.22320000000000007,4.4802867383512535,5
# [0, 646, 1068, 1472, 1842, 4879, 5515, 5685, 5782, 7220, 7433, 9172, 9207, 9236, 9676, 9992]
# [0, 987, 974, 972, 949, 856, 779, 715, 607, 483, 436, 422, 234, 215, 124, 116]