"""Task Sets - Manually Defined"""

from avr_fxns import avr_task

class UserTaskSet:

    """Manual task set"""

    def __init__(self):

        w_user_task_set = [0, 1000, 2000, 2100, 2200, 2500]
        c_user_task_set = [0, 515, 512, 490, 470, 200]
        a_user_task_set = 600000
        m_user_task_set = len(w_user_task_set)-1
        self.avr_task_instance_user_task_set = avr_task.AvrTask(
            m_user_task_set,w_user_task_set,c_user_task_set,a_user_task_set)
