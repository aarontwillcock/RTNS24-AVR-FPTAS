"""Set of delta values to iterate through"""

import copy

class DeltaSet:

    """Set of delta values to iterate through"""

    def __init__(self,delta_arr,desc):

        self.delta_arr = delta_arr
        self.desc = desc

    def update_delta_set_with_array(self,delta_arr):

        """Update current delta list with new"""

        self.delta_arr = copy.deepcopy(delta_arr)

    def update_delta_set_with_range(self,start_time,time_increment,max_time):

        """Update current delta list with new"""

        self.delta_arr = []
        for x in range(start_time,max_time+time_increment,time_increment):
            self.delta_arr += [x]

    def update_desc(self,desc):

        """Update description of delta set"""

        self.desc = desc
