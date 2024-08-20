"""Side-by-side Task Runner"""

import datetime
import time
import tracemalloc
import copy

from bpckp_fxns import bpckp_fptas
from bpckp_fxns import kavr_24 as KAVR_24
from bpckp_fxns import kavr_18 as KAVR_18
from bpckp_fxns import row_17 as ROW_17
from csv_fxns import csv_fxns
from apx_fxns import apx_obj

#pylint: disable=C0200

class ExperimentRunner:

    """Experiment Runner"""

    def __init__(self):

        self.runs_lifetime = 0
        self.fn_relative_location = "exp_data/"

    def create_base_file_name_from_exp(self,exp,exp_desc):

        """Create base filename from experiment parameters"""

        #Name Template: exp-algorithm--precision-store-memo-task_set-delta_set
        alg = exp.algorithm
        precision = exp.algorithm_params.precision
        memoization=exp.algorithm_params.memoize
        give_sln_seq=exp.algorithm_params.give_sln_seq
        trace=exp.algorithm_params.trace_memory
        task_set_desc = exp.avr_task_instance.desc
        delta_set_desc = exp.delta_set.desc
        csv_name_arr = [
            alg,
            "p"+str(precision),
            task_set_desc,
            delta_set_desc,
            "memo-"+str(int(memoization)),
            "slnSeq-"+str(int(give_sln_seq)),
            "trace-"+str(int(trace))
        ]

        base_name = exp_desc + "-"
        for param in csv_name_arr:
            base_name += param + "-"
        base_name = base_name[:len(base_name)-1]

        return base_name

    def print_headers_to_csv(self,headers,csv_handle):

        """Print csv file header row"""

        num_cols = len(headers)
        assert num_cols >= 1

        csv_header_str = ""

        for header_str in headers:
            csv_header_str += header_str + ","

        csv_header_str = csv_header_str[:len(csv_header_str)-1]
        csv_header_str += "\n"

        csv_handle.write(csv_header_str)
        csv_handle.flush()

    def begin_csv_log(self,file_base_name,headers,use_timestamps):

        """Create csv handle for file and print headers of csv"""

        (file_name,_,_) = csv_fxns.create_fn(file_base_name,self.fn_relative_location,use_timestamps)

        file_csv_handle = open(str(file_name),"w+",encoding="utf-8")

        self.print_headers_to_csv(headers,file_csv_handle)

        return file_csv_handle

    def agg_multiple_algs_against_apx(self,exps,non_apx_alg_list,precision_list,make_dbf_files,make_exp_files,make_agg_file,exp_desc,verbose,use_timestamps=False):

        num_exps = len(exps)

        for exp in exps:
            assert len(exp.delta_set.delta_arr) == 1

        #Setup file from first experiment
        (comp_file_base_name,comp_file_headers,csv_output) = self.run_multiple_algs_against_apx(exps[0],non_apx_alg_list,precision_list,make_dbf_files,make_exp_files,make_agg_file,exp_desc,verbose,use_timestamps)

        #Create file handle
        comp_file_handle = self.begin_csv_log(comp_file_base_name,comp_file_headers,use_timestamps)

        #Print first line
        self.print_csv_row_to_csv(csv_output,comp_file_handle)

        #Gather remainder of data
        for i in range(1,num_exps):

            (_,_,csv_output) = self.run_multiple_algs_against_apx(exps[i],non_apx_alg_list,precision_list,make_dbf_files,make_exp_files,make_agg_file,exp_desc,verbose,use_timestamps)
            self.print_csv_row_to_csv(csv_output,comp_file_handle)

    def run_multiple_algs_against_apx(self,base_apx_exp,non_apx_alg_list,precision_list,make_dbf_files,make_exp_files,make_agg_file,exp_desc,verbose,use_timestamps=False):

        """Run additional algorithms against a base APX experiment"""

        #Verify the base experiment is APX, that other supplied algs exist and are not APX
        assert base_apx_exp.algorithm == "apx"
        assert len(non_apx_alg_list) > 0
        assert "apx" not in non_apx_alg_list

        #Create complete alg list
        alg_list = non_apx_alg_list + ["apx"]
        num_algs = len(alg_list)

        #Prepare to store all data for each alg run
        delta_table_arr = [-1]*num_algs

        #For every candidate alg...
        for i in range(num_algs):

            #Create an altered experiment
            altered_exp = copy.deepcopy(base_apx_exp)
            altered_exp.algorithm = alg_list[i]
            altered_exp.precision = precision_list[i]

            #Execute and store
            delta_table_arr[i] = self.run_experiments([altered_exp],make_dbf_files,make_exp_files,make_agg_file,exp_desc,verbose,use_timestamps)

        #Create the header for the comparison CSV
        comp_file_headers = ["\\delta(us)"]

        #   Add these headers repeatedly -- one for each algorithm
        per_algorithm_base_file_headers = ["Demand(us)", "Runtime(s)", "C.Runtime(s)" "PRECISION(#)"]
        per_algorithm_file_headers_len = len(per_algorithm_base_file_headers)
        for i in range(num_algs):
            alg_name = alg_list[i]
            for j in range(per_algorithm_file_headers_len):
                comp_file_headers += [alg_name + per_algorithm_base_file_headers[j]]

        #Add APX headers
        comp_file_headers += ["e_r","e_b","e_f","1-E","Sln Multiplier"]


        #   Add these headers repeatedly -- one for each algorithm
        per_alg_apx_file_headers = ["Demand Ratio: APX / "]
        for i in range(num_algs):
            alg_name = alg_list[i]
            comp_file_headers += [per_alg_apx_file_headers[i] + alg_name]

        #Complete header construction with log time
        comp_file_headers += ["Log time(YYYY-MM-DD-HH-MN-SS)"]

        #Alter a copy of base experiment to change CSV name
        naming_specific_experiment = copy.deepcopy(base_apx_exp)
        naming_specific_experiment.algorithm = "multi"

        #Create CSV name and handle
        csv_file_base_name = self.create_base_file_name_from_exp(naming_specific_experiment,exp_desc)
        comp_file_base_name = csv_file_base_name + "-AG"
        # comp_file_csv_handle = self.begin_csv_log(comp_file_base_name,comp_file_headers,use_timestamps)

        #Extract set of \\delta values
        delta_set=base_apx_exp.delta_set.delta_arr

        #Extract apx instance
        apx_instance = base_apx_exp.algorithm_params.apx_params

        #Prepare CSV data to pass to agg
        csv_title = comp_file_headers
        csv_output = [-1]

        #For every delta value the experiments used...
        for i in range(len(delta_set)):

            #Get delta value and append to row
            delta_us = delta_set[i]
            comp_csv_row_data = [delta_us]

            #Clear the array of per-algorithm data
            demand_us_arr = [-1]*num_algs
            runtime_s_arr = [-1]*num_algs
            c_runtime_s_arr = [-1]*num_algs
            precision_arr = [-1]*num_algs
            apx_demand = -1

            #Append per-algorithm demand, runtime, precision data
            for j in range(num_algs):
                demand_us_arr[j] = delta_table_arr[j][i][1]
                runtime_s_arr[j] = delta_table_arr[j][2]
                c_runtime_s_arr[j] = delta_table_arr[j][i][3]
                precision_arr[j] = precision_list[j]
                comp_csv_row_data += [demand_us_arr[j],runtime_s_arr[j],c_runtime_s_arr[j],precision_arr[j]]
                if alg_list[j].lower() == "apx":
                    apx_demand = demand_us_arr[j]

            #Append approximation parameters
            comp_csv_row_data += [apx_instance.epsilon_r,apx_instance.epsilon_b,
                apx_instance.epsilon_f,apx_instance.one_minus_epsilon,
                apx_instance.solution_multiplier]

            #Append per-algorithm demand ratio data 
            for j in range(num_algs):
                alg_demand_ratio = apx_demand/demand_us_arr[j]
                comp_csv_row_data += [alg_demand_ratio]

            #Print info
            # self.print_csv_row_to_csv(comp_csv_row_data,comp_file_csv_handle)
            csv_output += comp_csv_row_data + "\n"

        return (comp_file_base_name,comp_file_headers,csv_output)

    def run_experiments(self,exp_list,make_dbf_files,make_exp_files,make_agg_file,exp_desc,verbose,use_timestamps=False):

        """Execute a set of experiments generating CSV output files"""

        #Return if no lists
        if len(exp_list) == 0:
            return

        #Default no csv handles
        dbf_file_csv_handle = -1
        agg_file_csv_handle = -1
        exp_file_csv_handle = -1

        if make_dbf_files or make_exp_files or make_agg_file:

            last_alg = exp_list[0].algorithm.lower()

            for exp in exp_list:
                current_alg = exp.algorithm.lower()
                if current_alg != last_alg:
                    print("Error: Not all algorithms are the same")
                    assert False
                else:
                    last_alg = current_alg

            task_file_base_name = self.create_base_file_name_from_exp(exp_list[0],exp_desc)
        else:
            task_file_base_name = -1

        if make_agg_file:
            agg_file_headers = ["\\delta(us)","Demand(us)",
            "Runtime(s)","C.Runtime(s)","M(#)","W(RPM)","C(us)",
            "A(RPM^2)","DELTA_SET(us)","PRECISION(#)","MAX RAM(bytes)",
            "e_r","e_b","e_f","1-E","Sln Multiplier","Log time(YYYY-MM-DD-HH-MN-SS)"]

            agg_file_base_name = task_file_base_name + "-AG"

            agg_file_csv_handle = self.begin_csv_log(agg_file_base_name,agg_file_headers,use_timestamps)

        if make_exp_files:

            exp_file_headers = ["M(#)","W(RPM)","C(us)","A(RPM^2)",
            "DELTA_SET(us)","PRECISION(#)","MAX RAM(bytes)",
            "e_r","e_b","e_f","1-E","Sln Multiplier","Log time(YYYY-MM-DD-HH-MN-SS)"]

            exp_file_base_name = task_file_base_name + "-ES"

            exp_file_csv_handle = self.begin_csv_log(exp_file_base_name,exp_file_headers,use_timestamps)

        num_exps = len(exp_list)

        exp_delta_table_arr = [-1]*num_exps

        for exp_index in range(num_exps):

            #Delay for 1s to enforce different files being created
            time.sleep(1)

            if verbose==1 and exp_index % 10 == 0:
                print("EXP RUNNER: ",exp_index+1,"/",num_exps)
            elif verbose == 2:
                print("EXP RUNNER:",exp_index+1,"/",num_exps)

            if make_dbf_files:

                dbf_file_headers = ["\\delta(us)","Demand(us)",
                "Runtime(s)","C.Runtime(s)","Log time(YYYY-MM-DD-HH-MN-SS)"]

                dbf_file_base_name = task_file_base_name + "-DR"

                dbf_file_csv_handle = self.begin_csv_log(dbf_file_base_name,dbf_file_headers,use_timestamps)

            exp_delta_table_arr[exp_index] = self.run_experiment(exp_list[exp_index],
                dbf_file_csv_handle,exp_file_csv_handle,agg_file_csv_handle,verbose)
        
        return exp_delta_table_arr

    def print_csv_row_to_csv(self,csv_row_data,csv_handle):

        """Print array of data to csv as comma-separated data"""

        csv_row_data_output_str = ""

        for data in csv_row_data:
            csv_row_data_output_str += str(data) +","

        str_24_hr_time = self.get_24_hr_date_time_str()
        csv_row_data_output_str += "-" + str_24_hr_time

        csv_row_data_output_str += "\n"

        csv_handle.write(csv_row_data_output_str)
        csv_handle.flush()

    def get_24_hr_date_time_str(self):

        """Return current 24-hour (military) date and time as string"""

        today = datetime.date.today()
        now = datetime.datetime.now()
        get_24_hr_date_time_str = str(today)+now.strftime("%H-%M-%S")
        return get_24_hr_date_time_str

    def make_array_csv_str(self,arr):

        """Return string format of array compatible with printing to csv file"""

        return "\"" + str(arr) + "\""

    def run_experiment(self,exp,
        dbf_file_csv_handle,exp_file_csv_handle,agg_file_csv_handle,verbose):

        """Run an individual experiment and log data where handles provided"""

        alg = exp.algorithm
        precision = exp.algorithm_params.precision
        memoization=exp.algorithm_params.memoize
        give_sln_seq = exp.algorithm_params.give_sln_seq
        task_set = exp.avr_task_instance
        delta_set=exp.delta_set.delta_arr
        trace=exp.algorithm_params.trace_memory
        apx_instance = exp.algorithm_params.apx_params

        if apx_instance is None:
            apx_instance = apx_obj.ApxObj(0.5,0.5,0.5)
            apx_instance.epsilon_r = -1
            apx_instance.epsilon_f = -1
            apx_instance.epsilon_b = -1
            apx_instance.one_minus_epsilon = -1
            apx_instance.solution_multiplier = -1

        m = task_set.m
        w = task_set.omega
        c = task_set.wcet
        a = task_set.alpha

        alg = alg.lower()

        max_mem_usage = -1

        if alg == "apx": #Approximate
            bpckp_instance = bpckp_fptas.PdsBpckpFptas(task_set, apx_instance)
            delta_table = [[]]
            if trace:
                tracemalloc.start()
            delta_table = bpckp_instance.calculate_demand_seq(
            verbose, delta_set, True, True)
            if trace:
                mem_usage = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                max_mem_usage =  max(mem_usage)

        if alg == "exact": #Exact
            bpckp_instance = bpckp_fptas.PdsBpckpFptas(task_set, apx_instance)
            delta_table = [[]]
            if trace:
                tracemalloc.start()
            delta_table = bpckp_instance.calculate_demand_seq(
            verbose, delta_set, True, False)
            if trace:
                mem_usage = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                max_mem_usage =  max(mem_usage)

        if alg == "kavr24": #2024 KAVR
            kavr_instance = KAVR_24.Kavr2024(
            task_set,precision,memoization,give_sln_seq,verbose)
            delta_table = [[]]
            if trace:
                tracemalloc.start()
            delta_table = kavr_instance.calculate_exact_demand(delta_set)
            if trace:
                mem_usage = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                max_mem_usage =  max(mem_usage)

        if alg == "kavr18": #2018 KAVR
            kavr_instance = KAVR_18.Kavr2018(
            task_set,precision,memoization,give_sln_seq,verbose)
            delta_table = [[]]
            if trace:
                tracemalloc.start()
            delta_table = kavr_instance.calculate_exact_demand(delta_set)
            if trace:
                mem_usage = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                max_mem_usage =  max(mem_usage)

        if alg == "row17":
            row_instance = ROW_17.Row2017(
                task_set,precision,memoization,give_sln_seq,verbose)
            delta_table = [[]]
            if trace:
                tracemalloc.start()
            delta_table = row_instance.calculate_exact_demand(delta_set)
            if trace:
                tracemalloc.stop()
                max_mem_usage =  max(mem_usage)

        if dbf_file_csv_handle != -1:

            for i in range(len(delta_set)):

                delta_us = delta_set[i]
                demand_us = delta_table[i][1]
                runtime_s = delta_table[i][2]
                c_runtime_s = delta_table[i][3]

                dbf_csv_row_data = [delta_us,demand_us,runtime_s,c_runtime_s]

                self.print_csv_row_to_csv(dbf_csv_row_data,dbf_file_csv_handle)

        if exp_file_csv_handle != -1:

            w_str = self.make_array_csv_str(w)
            c_str = self.make_array_csv_str(c)
            delta_set_str = self.make_array_csv_str(delta_set)

            exp_csv_row_data = [m,w_str,c_str,a,delta_set_str,precision,max_mem_usage,
                apx_instance.epsilon_r,apx_instance.epsilon_b,
                apx_instance.epsilon_f,apx_instance.one_minus_epsilon,
                apx_instance.solution_multiplier]
            self.print_csv_row_to_csv(exp_csv_row_data,exp_file_csv_handle)

        if agg_file_csv_handle != -1:

            for i in range(len(delta_set)):

                delta_us = delta_set[i]
                demand_us = delta_table[i][1]
                runtime_s = delta_table[i][2]
                c_runtime_s = delta_table[i][3]

                w_str = self.make_array_csv_str(w)
                c_str = self.make_array_csv_str(c)
                delta_set_str = self.make_array_csv_str(delta_set)

                agg_csv_row_data = [delta_us,demand_us,runtime_s,c_runtime_s,
                    m,w_str,c_str,a,delta_set_str,precision,max_mem_usage,
                    apx_instance.epsilon_r,apx_instance.epsilon_b,
                    apx_instance.epsilon_f,apx_instance.one_minus_epsilon,
                    apx_instance.solution_multiplier]
                self.print_csv_row_to_csv(agg_csv_row_data,agg_file_csv_handle)

        return delta_table

