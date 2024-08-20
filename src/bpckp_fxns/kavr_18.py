"""Modified Bijinemula et al. RTSS '18 artifact to support test harness"""
import copy
import sys  #Exit command

from time import perf_counter #hi-res clock
from math import sqrt   #sqrt
from collections import defaultdict #Dictionary that does not throw KeyErrors
from bisect import bisect_left              #Provides would-be index of element to insert
sys.path.append("..")

class Kavr2018:

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
        self.dict_speed_accel = []

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

    #Acceleration Types accel_types
    #3 - speed \\in RBS, speed_new = speed, use var accel
    #2 - speed no in RBS, speed_new \\in RBS, use var accel
    #1 - use \\alpha^+

    def calc_min_time(self,speed,speed_new,accel_type):

        """Calculate MIAT given starting speed, next speed, and accel type"""

        #Pull terms from global
        # omega_arr = self.omega_arr
        # wcet_arr = self.wcet_arr
        a_max = self.a_max
        a_min = self.a_min

        #If speed is a RB speed and speed_new is equal to speed...
        if accel_type == 3:
            peak_speed = speed+a_max

            #If peak_speed does not exceed maximum speed...
            if peak_speed <= self.rbs_arr[-1]:
                #From Mohaqeqi et al. Eqn (20)
                # Accelerate maximally to peak_speed, decelerate maximally back to speed
                min_time = ((sqrt(peak_speed)-sqrt(speed))/a_max
                + (sqrt(speed)-sqrt(peak_speed))/a_min)

            #...otherwise peak_speed exceeds maximum speed.
            else:
                #Maintain constant speed
                min_time = 1/sqrt(speed)

            #Return minimum time in seconds
            return min_time*60

        #...otherwise, initial speed is not a RB speed.
        else:
            #From Mohaqeqi et al. Eqn (19) - Case 4 Rotational Speed
            peak_speed = (2*a_max*a_min+a_min*speed-a_max*speed_new)/(a_min-a_max)

            #If peak_speed does not exceed maximum speed...
            if peak_speed <= self.rbs_arr[-1]:
                #From Mohaqeqi et al. Eqn (20)
                # Accelerate maximally to peak_speed, decelerate maximally back to speed.
                min_time = ((sqrt(peak_speed)-sqrt(speed))/a_max
                + (sqrt(speed_new)-sqrt(peak_speed))/a_min)

            #...otherwise, peak_speed exceeds maximum speed.
            else:
                #From Mohaqeqi et al. Eqn (21)
                # Accelerate maximally to maximum allowable speed,
                # decelerate maximally back to speed.
                min_time = (((sqrt(self.rbs_arr[-1])-sqrt(speed))/a_max)
                    + ((1 - ((self.rbs_arr[-1]-speed)/(2*a_max))
                    -((speed_new-self.rbs_arr[-1])/(2*a_min)))/sqrt(self.rbs_arr[-1]))
                    + ((sqrt(speed_new)-sqrt(self.rbs_arr[-1]))/a_min))

            #Return minimum time in seconds
            return min_time*60

    #Function for calculating maximum demand given an initial speed over a set duration of time
    # - Bijinemula et al. Algorithm 1
    def calc_demand(self, speed, time, original_caller, depth):

        """Get max demand starting with speed, "speed", in time "time"""

        #Initialization
        demand_max = 0
        time = round(time,self.precision)

        #Stored demand check
        if self.memoization:
            if speed in self.dict_max_demand.keys():
                if time in self.dict_max_demand[speed].keys():
                    return self.dict_max_demand[speed][time]
                    # print("end of chain")

        #
        if 1 in self.dict_speed_accel[speed].keys():
            accel_type = 1
        else:
            accel_type = list(self.dict_speed_accel[speed].keys())[0]

        #If remaining time is less than minimum rotation time...
        if time < self.dict_speed_accel[speed][accel_type][1]:
            #Demand over remaining time is zero
            # print("end of chain")
            return (0,[[time]])

        #For each possible acceleration type...
        for accel_type in [3,2,1]:

            #If accel_type exists for the selected speed...
            if accel_type in self.dict_speed_accel[speed].keys():

                #Extract the new speed
                speed_new = self.dict_speed_accel[speed][accel_type][2]

                # if original_caller:
                    # print("Original Call on accel_type:",accel_type)

                #Calculate demand using saved value of initial speed
                # AND calculated demand of speed_new
                time_remaining = time-self.dict_speed_accel[speed][accel_type][1]
                package_returned = self.calc_demand(speed_new,time_remaining,False,depth+1)
                calc_demand_demand = package_returned[0]
                calc_demand_speed_pattern = package_returned[1]
                demand = self.dict_speed_accel[speed][accel_type][0] + calc_demand_demand

                #Update demand_max if needed
                if demand > demand_max:
                    # max_accel_type = accel_type
                    max_demand_speed_pattern = calc_demand_speed_pattern
                    current_max_speed = speed
                    demand_max = demand

        #Build return package
        if self.give_sln_seq:
            if current_max_speed == max_demand_speed_pattern[0][0]:
                max_demand_speed_pattern[0][1] = max_demand_speed_pattern[0][1] + 1
            else:
                max_demand_speed_pattern.insert(0,[current_max_speed,1])
        else:
            max_demand_speed_pattern = []
        package_to_return = (demand_max,max_demand_speed_pattern)

        #Save maximum demand to speed-time hash table
        if self.memoization:
            self.dict_max_demand[speed][time] = package_to_return
        # output = "Speed:" + format(speed,".1f") + " accel_type:" + str(max_accel_type)
        # output += " Demand:" + str(itemSet[speed][max_accel_type][0]) + " Time:"
        # output += + format(itemSet[speed][max_accel_type][1],".6f")
        # print(output)

        #Return maximum demand given initial speed and time window
        return package_to_return

    def delta_iterator_setup(self):

        """Populate ItemSet in preparation for iterative, demand-bound function calculation"""

        #Pull terms from global
        omega_arr = self.omega_arr
        wcet_arr = self.wcet_arr
        a_max = self.a_max
        a_min = self.a_min

        #Start timer
        self.start_time_cumulative = perf_counter()

        #Boundary Speeds
            #Squares of RB speeds used to avoid repeated sqrt computation later
            #Speeds in the first step are not counted per Lemma 2
            # - start from first RB speed
        self.rbs_arr =[speed**2 for speed in omega_arr[1:]]

        #Dictionary for logging speeds, accel_types, execution times, release times
        # - Supports dynamic programming.
        #Speeds in "itemSet" are saved as RPM
        #Template: itemSet[startSpeed][accel_type][wcet, timeToEndSpeed, endSpeed]

        #Case accel_types
        #3 - speed \\in RBS, speed_new = speed, use var accel
        #2 - speed no in RBS, speed_new \\in RBS, use var accel
        #1 - use \\alpha^+
        self.dict_speed_accel = defaultdict(dict)

        ##itemSet Population Routine
        #Iterate through all the RB speeds
        # to build the item list that is used to fill the Knapsack.
        for rbs in self.rbs_arr:   #O(m)

            #Select RB speeds in ascending order
            speed = rbs

            #Evaluate only ascending speed sequences - per Bijinemula et al. Lemma 2
            while speed<=self.rbs_arr[-1]:

                #If speed is RB speed AND not logged...
                if (speed in self.rbs_arr) and (sqrt(speed) not in self.dict_speed_accel.keys()):

                    #Set accel type to start at rb speed and ending w/ same speed
                    accel_type = 3

                    #Calculate release time in seconds
                    release_time = self.calc_min_time(speed, speed,accel_type)

                    #Index current speed
                    current_step = bisect_left(self.rbs_arr,speed)

                    #Assign execution time based on index
                    exec_time = self.wcet_arr[current_step]

                    #Log result
                    self.dict_speed_accel[sqrt(speed)][accel_type] = [exec_time, release_time,sqrt(speed)]

                #...otherwise, the speed is not a RB or is a logged RB.
                else:

                    #Calculate new speed at maximum acceleration
                    speed_new = speed+2*a_max

                    #Index the current speed
                    current_step = bisect_left(self.rbs_arr,speed)

                    #If speed_new exceeds the current RB and is not logged
                    faster_next_speed = speed_new > self.rbs_arr[current_step]
                    speed_not_logged_as_rb = sqrt(speed) not in self.dict_speed_accel.keys()
                    if (faster_next_speed) and (speed_not_logged_as_rb):

                        #Set accel type as start at non-RB speed w/ var accel
                        accel_type = 2

                        #Calculate release time in seconds
                        release_time = self.calc_min_time(speed,self.rbs_arr[current_step],accel_type)

                        #Assign execution time based on index
                        exec_time = wcet_arr[current_step]

                        #Log result
                        self.dict_speed_accel[sqrt(speed)][accel_type] = [exec_time, release_time,sqrt(self.rbs_arr[current_step])]

                        #If speed_new is less than maximum speed
                        if speed_new < self.rbs_arr[-1]:

                            #accel_type rotation as one with maximum acceleration
                            accel_type = 1

                            #Calculate release time in seconds
                            release_time = 60*((sqrt(speed_new)-sqrt(speed))/a_max)

                            #Log result
                            self.dict_speed_accel[sqrt(speed)][accel_type] = [exec_time, release_time,sqrt(speed_new)]

                            #Update speed for next iteration
                            speed = speed_new

                        #...otherwise, speed_new exceeds maximum allowable speed.
                        else:
                            #Exit the while loop, moving on to next RB
                            break

                    #...otherwise, speed_new does not exceed the current RB OR is not logged                                    
                    else:

                        #If speed_new exceeds the maximum allowable speed
                        if speed_new > self.rbs_arr[-1]:
                            #Exit the while loop, moving on to next RB
                            break

                        #otherwise, speed_new does not exceed the maximum allowable speed.

                        #accel_type rotation as one with maximum acceleration
                        accel_type = 1

                        #Calculate release time in seconds
                        release_time = 60*((sqrt(speed_new)-sqrt(speed))/a_max)

                        #Index the current speed
                        current_step = bisect_left(self.rbs_arr,speed)

                        #Assign execution time based on index
                        exec_time = wcet_arr[current_step]

                        #Log result
                        self.dict_speed_accel[sqrt(speed)][accel_type] = [exec_time, release_time,sqrt(speed_new)]

                        #Update speed
                        speed = speed_new

        #Push terms to global
        self.omega_arr = omega_arr
        self.wcet_arr = wcet_arr
        self.a_max = a_max
        self.a_min = a_min

    def calculate_exact_demand(self,list_of_deltas):

        """Get exact demand for AVR task given list of \\delta window sizes"""

        if self.verbose_print_level >=1:
            print("Method: KAVR'18")

        num_deltas = len(list_of_deltas)
        delta_table = [[-1 for i in range(4)] for j in range(num_deltas)]

        self.delta_iterator_setup()

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
            for rbs in self.rbs_arr:

                #Select RB speed
                speed = sqrt(rbs)

                #Calculate maximum demand starting from selected RB
                # print("Time:", tot_time, "Try: ",i)
                returned_package = self.calc_demand(speed,tot_time,True,0)
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
                output = "KAVR Delta " + str(d+1) + " of " + str(len(list_of_deltas))
                output += " | Delta: " + str(int(delta*1000*1000)) + " MIAT(us) "
                if self.give_sln_seq:
                    time_remaining = max_pattern[-1][0]
                    time_spent = delta - time_remaining
                    output +=str(round(time_spent*1000*1000,2))
                output +=" D(us): " + str(max_demand)
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
