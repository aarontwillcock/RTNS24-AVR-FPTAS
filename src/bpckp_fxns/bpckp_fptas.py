"""
Predefined Sequence (PDS)
Based Bounded Precedence Constraint Knapsack (BPCKP)
FPTAS for AVR Task Demand
Functions
"""

#pow,floor,ceiling
import math

#Performance counter - clock with highest available resolution
from time import perf_counter

RETURN_PACKAGE_ROUNDING_PRECISION = 12

USE_RET_PACKAGE = 0

class PdsBpckpFptas:

    """
    Predefined Sequence (PDS)
    Based Bounded Precedence Constraint Knapsack (BPCKP)
    FPTAS for AVR Task Demand
    Functions
    """

    def __init__(self,avr_task_instance,avr_apx):
        self.t_avr = avr_task_instance
        self.avr_apx = avr_apx
        self.max_index_thus_far_delta = 0
        self.max_index_thus_far = 0

    def calculate_demand_seq(self,print_progress,list_of_deltas,eff,apx):

        """ Calculate max demand in time \\delta using PDSs """

        mode = 3

        use_irf_analytic_miat = mode & 0b001
        elimination = mode & 0b010

        output_sig = ""

        if use_irf_analytic_miat:
            output_sig += "IRF-"

        if elimination:
            output_sig += "elim-"

        if print_progress:
            output_sig += "print-"

        if eff:
            output_sig +="eff-"

        if apx:
            output_sig += "approx-"

        if output_sig != "":
            print(output_sig)

        num_deltas = len(list_of_deltas)

        #Build table for logging runtimes
        delta_table = [[-1 for i in range(4)] for j in range(num_deltas)]

        start_ms_list = perf_counter()   #Start time for entire "dbf"

        # self.t_avr.disable_memoization()

        for delta_index in range(num_deltas):

            #Start timer
            start_sec = perf_counter()

            max_demand = 0

            delta_value = list_of_deltas[delta_index]

            max_util = self.t_avr.get_max_mode_utilization()

            #Begin binary search for max b which with MIAT <= delta
            b_lo = 0
            if eff:
                b_hi = math.ceil(delta_value * max_util)
            else:
                b_hi = delta_value

            while b_lo <= b_hi:

                b_search = (b_hi + b_lo) // 2

                # print(delta_value,b_search)

                if apx:
                    (miat,sln_seq,b_safe) = self.t_avr.fxn_t_ib_apx(
                                                self.t_avr.m,
                                                b_search,
                                                self.avr_apx,
                                                use_irf_analytic_miat,
                                                elimination)
                else:
                    (miat,sln_seq) = self.t_avr.fxn_t_ib(
                                        self.t_avr.m,
                                        b_search,
                                        use_irf_analytic_miat,
                                        elimination)

                if(miat <= delta_value and b_search > max_demand):
                    max_demand = b_search
                    max_demand_seq = sln_seq
                    max_demand_miat = miat
                    if apx:
                        b_safe_max = b_safe

                max_is_higher = miat <= delta_value

                if max_is_higher:

                    b_lo = b_search + 1

                else:

                    b_hi = b_search - 1

            #Time stop
            end_sec = perf_counter()

            print_output = (str(delta_value) + ","
                            + str(max_demand_miat) + "," + str(max_demand)
                            + "," + str(max_demand_seq))

            if apx:
                print_output += "," + str(b_safe_max)
            print(print_output)

            individual_delta_time = end_sec-start_sec
            cumulative_time = end_sec-start_ms_list

            delta_table[delta_index][0] = delta_value
            if apx:
                delta_table[delta_index][1] = b_safe_max
            else:
                delta_table[delta_index][1] = max_demand
            delta_table[delta_index][2] = individual_delta_time
            delta_table[delta_index][3] = cumulative_time

        self.t_avr.fxn_reset_all_tables()

        return delta_table
