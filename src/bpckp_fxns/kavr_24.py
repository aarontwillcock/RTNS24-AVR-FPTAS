"""Paper-based implementation of Bijinemula et al. RTSS '18"""
import copy
import sys  #Exit command

from time import perf_counter #hi-res clock
from math import sqrt   #sqrt
from collections import defaultdict #Dictionary that does not throw KeyErrors
sys.path.append("..")

class Kavr2024:

    """KAVR AVR Task Demand BPCKP Solver"""

    def __init__(self, avr_task_instance, precision, memoization, give_sln_seq, verbose_print_level):

        self.precision = precision
        self.memoization = memoization
        self.give_sln_seq = give_sln_seq
        self.verbose_print_level = verbose_print_level

        #Dictionary for logging speeds, completion times - Supports dynamic programming.
        self.dict_max_demand = defaultdict(dict)
        self.avr_task_instance = avr_task_instance

        #Timekeeping
        self.start_time_cumulative = -1

        #Item Set
        self.dict_calc_demand_speed_time = defaultdict(dict)

        #RB Speeds
        self.rbs_arr = []

        #Units
        #a_max, a_min : revolutions / min^2
        #speed, peak_speed, speed_new : revolutions / minute (RPM)

        #Acceleration equal in magnitude to deceleration per Bijinemula et al. Sec. III.A Para. 4
        a_max = self.avr_task_instance.alpha
        a_min = -a_max

        #Execution time values (micro seconds)
        # from Mohaqeqi et al. Table 18 - http://user.it.uu.se/~yi/pdf-files/2017/ecrts17.pdf
        wcet_arr = copy.deepcopy(self.avr_task_instance.wcet)
        wcet_arr.remove(0)

        #Sort RB Speeds in increasing order
        omega_arr = self.avr_task_instance.omega

        #Sort execution times in decreasing order
        wcet_arr.sort(reverse=True)

        #Validate # RB Speeds is one more than # Execution Times
        if len(omega_arr) != len(wcet_arr)+1:
            print('Error: The # boundary speeds != # WCETs + 1.')
            sys.exit(0)

        #Print Parameters:
        # print('omega_arr: ',omega_arr, 'revolutions / minute')
        # print('wcet_arr: ',wcet_arr, 'us')
        # print('a_max:          ',a_max, ' revolutions / min^2')
        # print('a_min:          ',a_min, 'revolutions / min^2')

        #Push terms to global
        self.omega_arr = omega_arr
        self.wcet_arr = wcet_arr
        self.a_max = a_max
        self.a_min = a_min

        self.dict_max_rotation = {}
        self.dict_calc_min_time = {}
        self.dict_c = {}
        self.dict_nps = {}

    def min_rotation_time(self,omega):

        """Get fastest MIAT achievable for job released at speed \\omega"""

        # if speed in dict_max_rotation:
        #     return dict_max_rotation[omega]

        alpha_max = self.a_max

        #Fastest reachable speed
        max_speed_no_limit = sqrt(omega**2 + 2*alpha_max)
        max_speed_limit_by_omega_m = min(max_speed_no_limit,self.omega_arr[-1])

        #MIAT to fastest reachable speed
        miat_sec = self.calc_min_time(omega,max_speed_limit_by_omega_m)

        self.dict_max_rotation[omega] = miat_sec

        return miat_sec

    def calc_min_time(self,speed,speed_new):

        """Calculate MIAT between two speeds"""

        # if (speed,speed_new) in dict_calc_min_time:
        #     return dict_calc_min_time[(speed,speed_new)]

        #setup vars like Bijinemula et. al. Eqn 3.
        omega = speed
        f = speed_new
        alpha_max = self.a_max

        #Bijinemula et. al. Eqn 3
        omega_p = sqrt((omega**2+f**2+self.a_max)/2)

        #setup vars like Bijinemula et. al. Eqn 4
        omega_max = self.omega_arr[-1]

        #Bijinemula et. al. Eqn 4
        if omega_p <= omega_max:

            miat_min = (sqrt(2*omega**2 + 2*f**2 + 4*alpha_max) - omega - f)/alpha_max

        else:

            miat_min = ((omega_max - f - omega)/(alpha_max)) + ((omega**2 + f**2)/(2*omega_max*alpha_max)) + (1/omega_max)

        #Get miat in seconds
        miat_sec = miat_min * 60

        self.dict_calc_min_time[(speed,speed_new)] = miat_sec

        #Return minimum time in seconds
        return miat_sec

    def c(self,omega):

        """Get WCET for jobs released at speed \\omega"""

        # if omega in dict_c:s

        wcet = -1

        for i in range(len(self.omega_arr)):

            if omega <= self.omega_arr[i]:

                wcet =  self.wcet_arr[i-1]
                break

        self.dict_c[omega] = wcet

        return wcet

    def next_possible_speeds(self,speed):

        """Get the set of reachable speeds from 'speed'
        (i.e., get the set of equivalent or higher speed RBs and the maximum reachable speed)"""

        # if speed in dict_nps:
        #     return dict_nps[speed]

        nps = []

        alpha_max = self.a_max

        max_speed_no_limit  = sqrt(speed**2 + 2*alpha_max)
        max_speed_limit_by_omega_m = min(max_speed_no_limit,self.omega_arr[-1])

        for rbs_x in self.omega_arr:

            if speed <= rbs_x <= max_speed_limit_by_omega_m:

                nps += [rbs_x]

        if max_speed_limit_by_omega_m != self.omega_arr[-1]:
            nps += [max_speed_limit_by_omega_m]

        self.dict_nps[speed] = nps

        return nps

    #Function for calculating maximum demand given an initial speed over a set duration of time
    # - Bijinemula et al. Algorithm 1
    def calculate_demand(self, omega, delta):

        """Calculate maximum demand that can be generated by a sequence of speeds
        beginning at speed \\omega over an interval of side \\delta seconds"""

        #Initialization
        max_demand = 0
        max_seq = []

        # delta_rounded = delta
        if self.precision == 0:
            delta_rounded = delta
        else:
            delta_rounded = round(delta,self.precision)

        #Stored demand check
        if self.memoization:
            if omega in self.dict_calc_demand_speed_time.keys():
                if delta_rounded in self.dict_calc_demand_speed_time[omega].keys():
                    return self.dict_calc_demand_speed_time[omega][delta_rounded]

        #If remaining time is less than minimum rotation time...
        if delta_rounded < self.min_rotation_time(omega):

            #No demand generated
            return (max_demand,max_seq)

        current_speed_wcet = self.c(omega)

        #For every reachable speed...
        for omega_prime in self.next_possible_speeds(omega):

            miat_omega_to_omega_prime = self.calc_min_time(omega,omega_prime)
            delta_remaining = delta_rounded - miat_omega_to_omega_prime

            (ret_demand_calc_d,ret_seq_calc_d) = self.calculate_demand(omega_prime,delta_remaining)
            demand_omega_prime = current_speed_wcet + ret_demand_calc_d

            if self.give_sln_seq:

                if ret_seq_calc_d == []:
                    seq = [[round(omega,2),1]]
                else:
                    if ret_seq_calc_d[0][0] == round(omega,2):
                        seq = ret_seq_calc_d
                        seq[0][1] +=1
                    else:
                        seq = [[round(omega,2),1]] + ret_seq_calc_d
            else:

                seq = []

            if demand_omega_prime > max_demand:
                max_demand = demand_omega_prime
                max_seq = seq

        if self.memoization:
            self.dict_calc_demand_speed_time[omega][delta_rounded] = (max_demand,max_seq)

        return (max_demand,max_seq)

    def calculate_exact_demand(self,list_of_deltas):

        """Get exact demand for AVR task given list of \\delta window sizes"""

        if self.verbose_print_level >=1:
            print("Method: KAVR'24")

        self.start_time_cumulative = perf_counter()

        num_deltas = len(list_of_deltas)
        delta_table = [[-1 for i in range(4)] for j in range(num_deltas)]

        ##Recursive Demand Calculation
        #Initialization
        max_demand = 0

        if list_of_deltas[-1] >= 10000000: #10s
            sys.setrecursionlimit(2000)

        #For every 0.01 time step in [0.01,1.01)
        for d in range(num_deltas):

            delta = list_of_deltas[d]

            #Convert to seconds
            delta = delta/1000000

            tot_time = delta

            start = perf_counter()

            max_pattern = (0,[0])

            #For every RB speed
            for rbs in self.omega_arr:

                #Calculate maximum demand starting from selected RB
                # print("Time:", tot_time, "Try: ",i)
                returned_package = self.calculate_demand(rbs,tot_time)
                demand = returned_package[0]
                pattern = returned_package[1]
                # print("\n")

                #Update maximum demand if needed
                if demand > max_demand:
                    max_demand = demand
                    max_pattern = pattern

            end = perf_counter()
            total_time = end - start
            cumulative_time = end - self.start_time_cumulative
            # output = "\delta = " + str(tot_time) + " D: "
            # output += str(max_demand) + " in " + str(round(total_time,2))
            # print(output)

            if self.verbose_print_level >=2:
                # time_remaining = max_pattern[-1][0]
                # time_spent = delta - time_remaining
                output = "KAVR Delta " + str(d+1) + " of " + str(len(list_of_deltas))
                output += " | Delta: " + str(int(delta*1000*1000))
                # output +=" MIAT(us) " + str(round(time_spent*1000*1000,2))
                output += " D(us): " + str(max_demand)
                output += " RT(s): " + str(total_time)
                if self.give_sln_seq:
                    output += " P: " + str(max_pattern)
                print(output)
            #If verbose requested write the demand for this time-step to file
            # if args.verbose:
            # f.write('Max demand for time: {} = {}\n'.format(tot_time,max_demand))

            delta_table[d][0] = delta
            delta_table[d][1] = max_demand
            delta_table[d][2] = total_time
            delta_table[d][3] = cumulative_time

        return delta_table
