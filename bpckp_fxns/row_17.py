"""Implementation of Mohaqeqi et al. AVR task DBF algorithm"""

#Dependencies
from time import perf_counter           #clock w/ highest resolution
from math import sqrt                   #Square root
from collections import defaultdict     #Dictionary that does not throw KeyErrors
from bisect import bisect_left          #Provides would-be index of element to insert
import sys                              #Exit command
import copy
import datetime

#pylint: disable=C0200,C0201
#pylint: disable=line-too-long

class Row2017:

    """ROW17 AVR Task Demand Solver"""

    def create_fn_w_timestamp(self,base):
        """Create file name with timestamp"""

        today = datetime.date.today()               #Get date
        postfix = "-" + str(today)                  #Add formatted date
        now = datetime.datetime.now()               #Get Time
        current_time = now.strftime("%H-%M-%S")     #Convert time to formatted string
        postfix += "-" + str(current_time)          #Add formatted time to filename
        postfix += ".txt"                           #Append suffix
        prefix = "exp_data/"                        #Create prefix
        full_file_name = prefix + base + postfix    #Append directory
        file_name = base + postfix
        return (full_file_name,file_name,prefix,postfix)        #Return completed Filename

    def __init__(self,avr_task_instance,precision,memoization,give_sln_seq,verbose_print_level):

        self.precision = precision
        self.memoization = memoization
        self.give_sln_seq = give_sln_seq
        self.verbose_print_level = verbose_print_level

        self.avr_task_instance = avr_task_instance

        #Dictionary for logging speeds, completion times - Supports dynamic programming.
        self.dict_max_demand = defaultdict(dict)

        self.start_time_cumulative = -1

        #Units
        #A_MAX, A_MIN - revolutions / min^2
        #speed, peak_speed, speed_new - revolutions / minute (RPM)

        #Acceleration equal in magnitude to deceleration per Bijinemula et al. Sec. III.A Para. 4
        self.a_max = self.avr_task_instance.alpha
        self.a_min = -self.a_max

        #Execution time values (micro seconds) from Mohaqeqi et al. Table 18 - http://user.it.uu.se/~yi/pdf-files/2017/ecrts17.pdf
        self.wcet_arr = copy.deepcopy(self.avr_task_instance.wcet)
        self.wcet_arr.remove(0)

        #Sort Right Boundary Speeds in increasing order
        self.omega_arr = self.avr_task_instance.omega
        self.omega_arr_squared = -1

        self.adjacency_matrix = -1
        self.nodes = -1

        #Validate # Right Boundary Speeds is one more than # Execution Times
        if len(self.omega_arr) != len(self.wcet_arr)+1:
            print('Error: The number of boundary speeds should be one more than the number of execution times.')
            sys.exit(0)

    #Function for calculating maximum demand given a starting node over a set duration of time
    def calc_demand(self,i,time):

        """Calculate maximum demand when starting a speed sequence at vertex i
        over an interval of size 'time' (in seconds)"""

        #Initialization
        demand_max = 0
        seq_max = []

        if self.precision == 0:
            time_rounded = time
        else:
            time_rounded = round(time,self.precision)

        #Stored demand check
        if self.memoization:
            if i in self.dict_max_demand.keys():
                if time_rounded in self.dict_max_demand[i].keys():
                    return self.dict_max_demand[i][time_rounded]

        #If node is not the first right boundary speed...
        if self.nodes[i][1]!=self.omega_arr_squared[0]:
            #Assign execution time based on index
            dem_node = self.wcet_arr[bisect_left(self.omega_arr_squared,self.nodes[i][1])-1]
        #...otherwise, assign first execution time
        else:
            dem_node = self.wcet_arr[0]

        #Iterate through all nodes
        for j in range(len(self.nodes)):

            #If the node pair selected is reachable from each other...
            if (i,j) in self.adjacency_matrix.keys():

                #Extract the time required to reach the next node
                time_next_node = self.adjacency_matrix[(i,j)]

                #If insufficient time remains to reach the next node...
                if time_rounded - time_next_node < 0:
                    #Do not count towards demand, try next node
                    continue

                #If time remaining is exactly the required time...
                if time_rounded - time_next_node == 0:
                    #Update demand if necessary and continue
                    if dem_node > demand_max:
                        demand_max = dem_node
                        continue

                #Calculate new demand
                (ret_demand_calc_d,ret_seq_calc_d) = self.calc_demand(j,time_rounded-time_next_node)
                demand = dem_node + ret_demand_calc_d

                if self.give_sln_seq:

                    if ret_seq_calc_d == []:
                        seq = [[round(sqrt(self.nodes[i][1]),2),1],time_rounded-time_next_node]
                    else:
                        if ret_seq_calc_d[0][0] == round(sqrt(self.nodes[i][1]),2):
                            seq = ret_seq_calc_d
                            seq[0][1] += 1
                        else:
                            seq = [[round(sqrt(self.nodes[i][1]),2),1]] + ret_seq_calc_d

                else:

                    seq = []

                #Update demand if necessary
                if demand > demand_max:
                    demand_max = demand
                    seq_max = seq

        #Update hash table with max demand and return
        if self.memoization:
            self.dict_max_demand[i][time_rounded] = (demand_max,seq_max)

        return (demand_max,seq_max)

    def delta_iterator_setup(self):

        """Create nodes required for ROW'17 to run"""

        a_max = self.a_max
        a_min = self.a_min

        #Start timer
        self.start_time_cumulative = perf_counter()

        #Boundary Speeds
            #Squares of right boundary speeds used to avoid repeated sqrt computation later
            #Speeds in the first step are not counted per Lemma 2 - start from first right boundary speed
        self.omega_arr_squared = [speed**2 for speed in self.omega_arr]
        max_speed = self.omega_arr_squared[-1]

        #Setup node_speeds
        node_speeds = set()

        #Iterate through all boundary speeds, creating nodes for all reachable speeds
        for x in range(len(self.omega_arr_squared)):
            speed = self.omega_arr_squared[x]           #Select boundary speed
            while speed <= max_speed:            #While speed has not exceed max speed
                node_speeds.add(speed)               #Create node for speed
                speed = speed + 2*a_max             #Add subsequent, increasing speed via a_max

            speed = self.omega_arr_squared[x]           #Select boundary speed
            while speed>=self.omega_arr_squared[0]:     #While speed has not fallen below the lowest boundary speed
                node_speeds.add(speed)               #Create node for speed
                speed = speed + 2*a_min             #Add subsequent, decreasing speed via a_min
        node_speeds = sorted(node_speeds)         #Nodes sorted by speed increasing order

        #Setup nodes
        self.nodes = []

        for i,j in zip(node_speeds[:-1],node_speeds[1:]): #For each tuple in a list of created tuples
            self.nodes.append((i,j))                             #Add each tuple to nodes

        self.adjacency_matrix = dict()  #Empty adjacency matrix for creating DRT graph

        for i in range(len(self.nodes)):                 #For every node tuple
            current_node = self.nodes[i][1]                     #Select right boundary
            for j in range(i,len(self.nodes)):               #Iterate through all possible next right boundaries
                next_node = self.nodes[j][1]                        #Select next right boundary
                max_reach = current_node + 2*a_max              #Calculate maximum next speed

                #If next right boundary is not reachable, break
                if next_node > max_reach:
                    break

                #If next right boundary is reachable via constant a_max...
                if next_node == max_reach:
                    #Calculate minimum interarrival time - Mohaqeqi et al. Sec. 3.2 Case 2
                    self.adjacency_matrix[(i,j)] = 60*(sqrt(next_node)-sqrt(current_node))/a_max

                #...otherwise, the next right boundary is reachable via variable acceleration
                else:
                    #Calculate the prospective peak speed
                    mid_speed = (2*a_min*a_max+a_min*current_node-a_max*next_node)/(a_min-a_max)

                    #If the prospective peak speed does not exceed maximum speed...
                    if mid_speed <= max_speed:
                        #Calculate3 minimum interarrival time in seconds - Mohaqeqi et al. Sec 3.2 Eqn 20
                        self.adjacency_matrix[(i,j)] = 60*((sqrt(mid_speed)-sqrt(current_node))/a_max +(sqrt(next_node)-sqrt(mid_speed))/a_min)

                    #...otherwise, the prospective peak speed exceeds maximum speed
                    else:
                        #Calculate the time to reach maximum speed - Mohaqeqi et al. Sec. 3.2 Eqn 21 t_1^*
                        t1 = (sqrt(max_speed) - sqrt(current_node))/a_max
                        #Calculate the time over which maximum speed is maintained - Mohaqeqi et al. Sec. 3.2 Eqn 21 t_2^*
                        t2 = (1-((max_speed-current_node)/(2*a_max))-((next_node-max_speed)/(2*a_min)))/sqrt(max_speed)
                        #Calculate the time to descend from maximum speed to final speed - Mohaqeqi et al. Sec. 3.2 Eqn 21 t_3^*
                        t3 = (sqrt(next_node)-sqrt(max_speed))/a_min

                        #Sum individual time segments and convert to seconds
                        self.adjacency_matrix[(i,j)] = 60*(t1 + t2 + t3)

                #Mirror adjacency matrix
                self.adjacency_matrix[(j,i)] = self.adjacency_matrix[(i,j)]

    def calculate_exact_demand(self,list_of_deltas):

        """Get exact demand for AVR task given list of \\delta window sizes"""

        if self.verbose_print_level >=1:
            print("Method: ROW'17")

        num_deltas = len(list_of_deltas)
        delta_table = [[-1 for i in range(4)] for j in range(num_deltas)]

        self.delta_iterator_setup()

        max_demand = 0

        #For every 0.01 time step in [0.01,1.00]
        for d in range(num_deltas):

            delta = list_of_deltas[d]

            #Convert to seconds
            time_sec = delta/1000000

            start = perf_counter()

            max_pattern = (0,[0])

            #For each node
            for i in range(len(self.nodes)):

                #Calculate maximum demand starting from the selected node
                returned_package = self.calc_demand(i,time_sec)
                demand = returned_package[0]
                pattern = returned_package[1]

                #Update maximum demand if needed
                if demand > max_demand:
                    max_demand = demand
                    max_pattern = pattern

            #End performance counting, calculate and log total time
            end = perf_counter()
            total_time = end - start
            cumulative_time = end - self.start_time_cumulative

            if self.verbose_print_level >=2:
                # time_remaining = max_pattern[-1][0]
                # time_spent = time_sec - time_remaining
                output = "ROW Delta " + str(d+1) + " of " + str(len(list_of_deltas))
                output += " | Delta: " + str(int(time_sec*1000*1000))
                # output += " MIAT(us) " + str(round(time_spent*1000*1000,2))
                output += " D(us): " + str(max_demand)
                output += " RT(s): " + str(total_time)
                if self.give_sln_seq:
                    output += " P: " + str(max_pattern)
                print(output)

            delta_table[d][0] = delta
            delta_table[d][1] = max_demand
            delta_table[d][2] = total_time
            delta_table[d][3] = cumulative_time

        return delta_table
