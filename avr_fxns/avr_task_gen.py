"""AVR task generation functions"""

import random
from . import avr_task

class AvrTaskGen:

    """AVR task generation class"""

    def __init__(self,m_b,w_b,c_b,a_b):
        self.m_b = m_b
        self.w_b = w_b
        self.c_b = c_b
        self.a_b = a_b

    def update_bounds(self,m_b,w_b,c_b,a_b):

        """Update bounds on m,w,c,a"""

        self.m_b = m_b
        self.w_b = w_b
        self.c_b = c_b
        self.a_b = a_b

    def generate_avr_task(self):

        """Generate AVR task parameters"""

        #AVR Model Definition
        #   Modes
        m = random.randint(self.m_b[0], self.m_b[1])
        #   Speeds (rpm)
        w = [-1]*(m+1)
        w[0] = 0
        for i in range(m):
            w[i+1] = random.randint(self.w_b[0], self.w_b[1])
        w.sort()
        #   wcet (ms)
        c = [-1]*(m)
        for i in range(m):
            c[i] = random.randint(self.c_b[0], self.c_b[1])
        c.sort(reverse=True)
        c.insert(0,0)
        #   acceleration
        a = random.randint(self.a_b[0], self.a_b[1])

        #Create AVR Task
        avr_task_instance = avr_task.AvrTask(m, w, c, a)

        #Return Task
        return avr_task_instance

    def generate_feasible_avr_task(self, max_attempts):

        """Generate feasible AVR task parameters"""

        attempts = 0

        task_acceptable = False

        while task_acceptable is False:

            possible_task = self.generate_avr_task()

            feasible = self.is_task_feasible(possible_task)
            if not feasible:
                print("Infeasible Generation")
            properly_formed = self.is_task_formed_properly(possible_task)
            if not properly_formed:
                print("Not Properly Formed Generation")

            if feasible and properly_formed:
                task_acceptable = True
            else:
                attempts += 1

                if attempts > max_attempts:

                    assert False

        return possible_task

    def is_task_feasible(self,avr_task_instance):

        """Determine whether avr task is feasible"""

        return avr_task_instance.is_feasible()

    def is_task_formed_properly(self,avr_task_instance):

        """Determine whether avr task has proper form"""

        for i in range(avr_task_instance.m-1):

            if avr_task_instance.omega[i] == avr_task_instance.omega[i+1]:
                print("Equivalent Speeds")
                return False

        for i in range(avr_task_instance.m-1):

            if avr_task_instance.wcet[i] == avr_task_instance.wcet[i+1]:
                print("Equivalent WCET")
                return False

        for i in range(1,avr_task_instance.m-1+1):

            #Calculate number of jobs between RBs
            distance = avr_task_instance.fxn_theta(i, i+1)

            #If distance is less than one rotation (i.e., does not conform to KAVR), reject it
            if distance < 1:

                print("Distance Less than 1 Rotation")
                return False

        return True
