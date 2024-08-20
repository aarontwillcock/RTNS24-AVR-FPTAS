"""Side-by-side Task Runner"""

import datetime
import time
import tracemalloc

from bpckp_fxns import bpckp_fptas
from bpckp_fxns import kavr_24 as KAVR_24
from bpckp_fxns import kavr_18 as KAVR_18
from bpckp_fxns import row_17 as ROW_17
from csv_fxns import csv_fxns
from apx_fxns import apx_obj

#pylint: disable=C0200

USE_TIMESTAMPS_DEFAULT = True

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

    def run_experiments(self,exp_list,make_dbf_files,make_exp_files,make_agg_file,exp_desc,verbose,use_timestamps=USE_TIMESTAMPS_DEFAULT):

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

            self.run_experiment(exp_list[exp_index],
                dbf_file_csv_handle,exp_file_csv_handle,agg_file_csv_handle,verbose)

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
                mem_usage = tracemalloc.get_traced_memory()
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
