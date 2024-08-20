"""Side-by-side Task Runner"""

import datetime
import tracemalloc

from avr_fxns import avr_task
from bpckp_fxns import bpckp_fptas
from bpckp_fxns import kavr_24 as KAVR_24
from bpckp_fxns import kavr_18 as KAVR_18
from csv_fxns import csv_fxns
from sxs_fxns import sxs_task

NUM_METHODS = 5 #row18,kavr18,kavr24,exact,apx

AR_ROUND_PREC = 4

class SxsRunner:

    """Side-by-side runner"""

    def __init__(self,num_sxs_tasks):

        self.tasks_run = 0
        self.method_time_results = [0]
        self.method_time_results = [0]

    def run_tasks_side_by_side(
        self,sxs_task_list,create_individual_task_files,
        create_sxs_task_file,base_name_descriptor,single_file_for_random_tests,
        enable_memory_tracing):

        """Execute tasks side by side"""

        verbose = bool(len(sxs_task_list) >= 50)

        if single_file_for_random_tests:

            sxs_index = 0
            base_name = "sxs_comb_run-" + str(base_name_descriptor) + "-idx-" + str(sxs_index)
            if sxs_index == 0:
                (file_name,prefix,postfix) = csv_fxns.create_fn_w_timestamp(base_name)
            else:
                file_name = prefix + base_name + postfix
            csv_file_combined = open(str(file_name),"a+",10, encoding="utf-8")

            #Printing First Row of COMBINED \delta file
            sxs_csv_output_data_headers = ["\\delta",
            "DRT Demand Calc","DRT Single Time","DRT Total Time",
            "KAVR18 Demand Calc","KAVR18 Single Time","KAVR18 Total Time","KAVR18 Precision",
            "KAVR24 Demand Calc","KAVR24 Single Time","KAVR24 Total Time","KAVR24 Precision",
            "KAVR=EXT",
            "EXT Demand Calc","EXT Single Time","EXT Total Time",
            "APX Demand Calc","APX Single Time","APX Total Time",
            "APX/KAVR Demand","APX/EXT Demand",
            "e_r","e_f","e_b","1-E","Solution Multiplier"]
            num_data_points = len(sxs_csv_output_data_headers)
            sxs_csv_output_data = [-1]*num_data_points
            sxs_csv_output_string = ""

            for i in range(num_data_points):
                sxs_csv_output_string += str(sxs_csv_output_data[i])
                if i+1 < num_data_points:
                    sxs_csv_output_string += ","
            sxs_csv_output_string += "," + "Log Time\n"
            csv_file_combined.write(sxs_csv_output_string)
            csv_file_combined.flush()

        if create_sxs_task_file:
            base_name = "sxs_tasks-" + base_name_descriptor
            (file_name,prefix,postfix) = csv_fxns.create_fn_w_timestamp(base_name)
            csv_file_sxs_tasks_all = open(str(file_name),"a+",10,encoding="utf-8")
            sxs_csv_row_data_headers = ["max_delta",
                "DRT_time","KAVR18_time","KAVR24_time","EXACT_time","APX_time",
                "start_time","time_increment","max_time",
                "units/us","M","W","C","A","e_r","e_b","e_f","1-E",
                "Solution Multiplier",
                "KAVR18_PRECISION","KAVR24_PRECISION",
                "DRT_RAM","KAVR18_RAM","EXACT_RAM","APX_RAM"]
            num_data_points = len(sxs_csv_row_data_headers)
            sxs_csv_row_data = [-1]*num_data_points
            sxs_csv_output_string = ""
            for i in range(num_data_points):
                sxs_csv_output_string += str(sxs_csv_row_data[i])
                if i+1 < num_data_points:
                    sxs_csv_output_string += ","
            sxs_csv_output_string += "\n"
            csv_file_sxs_tasks_all.write(sxs_csv_output_string)
            csv_file_sxs_tasks_all.flush()

        num_sxs_tasks = len(sxs_task_list)
        for sxs_index in range(num_sxs_tasks):

            if verbose and sxs_index % 10 == 0:
                print("SXS_RUNNER: ",sxs_index,"/",num_sxs_tasks)

            if create_individual_task_files:
                base_name = "sxs_run-" + str(base_name_descriptor) + "-" + str(sxs_index)
                if sxs_index == 0:
                    (file_name,prefix,postfix) = csv_fxns.create_fn_w_timestamp(base_name)
                else:
                    file_name = prefix + base_name + postfix
                csv_file = open(str(file_name),"a+",10,encoding="utf-8")

            current_sxs_task = sxs_task_list[sxs_index]
            exe_drt = current_sxs_task.method_set[0]
            exe_kavr18 = current_sxs_task.method_set[1]
            exe_kavr24 = current_sxs_task.method_set[2]
            exe_exact = current_sxs_task.method_set[3]
            exe_apx = current_sxs_task.method_set[4]
            avr_task_instance = current_sxs_task.avr_task_instance
            avr_apx = current_sxs_task.apx_obj_instance
            list_of_deltas = current_sxs_task.delta_set.list_of_deltas
            num_deltas = len(list_of_deltas)
            sxs_csv_row_data = [-1]*23
            sxs_csv_row_data[0] =   list_of_deltas[-1]
            sxs_csv_row_data[5] =   current_sxs_task.delta_set.start_time
            sxs_csv_row_data[6] =   current_sxs_task.delta_set.time_increment
            sxs_csv_row_data[7] =   current_sxs_task.delta_set.max_time
            sxs_csv_row_data[8] =   current_sxs_task.delta_set.units_per_us
            sxs_csv_row_data[9] =   avr_task_instance.m
            sxs_csv_row_data[10] =  "\"" + str(avr_task_instance.omega) + "\""
            sxs_csv_row_data[11] =  "\"" + str(avr_task_instance.wcet) + "\""
            sxs_csv_row_data[12] =  avr_task_instance.alpha
            sxs_csv_row_data[13] =  current_sxs_task.apx_obj_instance.epsilon_r
            sxs_csv_row_data[14] =  current_sxs_task.apx_obj_instance.epsilon_b
            sxs_csv_row_data[15] =  current_sxs_task.apx_obj_instance.epsilon_f
            sxs_csv_row_data[16] =  current_sxs_task.apx_obj_instance.one_minus_epsilon
            sxs_csv_row_data[17] =  current_sxs_task.apx_obj_instance.solution_multiplier
            sxs_csv_row_data[18] =  current_sxs_task.kavr_config.kavr_precision

            kavr_precision = current_sxs_task.kavr_config.kavr_precision
            kavr_store_demand = current_sxs_task.kavr_config.kavr_store_demand
            print_level = current_sxs_task.print_config

            if exe_apx: #Approximate
                sxs_bpckp = bpckp_fptas.PdsBpckpFptas(avr_task_instance, avr_apx)
                delta_table_approximate = [[]]
                if enable_memory_tracing:
                    tracemalloc.start()
                delta_table_approximate = sxs_bpckp.calculate_demand_seq(
                print_level, list_of_deltas, True, True)
                if enable_memory_tracing:
                    mem_usage = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                cumulative_time = delta_table_approximate[-1][3]
                sxs_csv_row_data[4] = cumulative_time
                if enable_memory_tracing:
                    sxs_csv_row_data[22] =  max(mem_usage)

            if exe_exact: #Exact
                sxs_bpckp = bpckp_fptas.PdsBpckpFptas(avr_task_instance, avr_apx)
                delta_table_exact = [[]]
                if enable_memory_tracing:
                    tracemalloc.start()
                delta_table_exact = sxs_bpckp.calculate_demand_seq(
                print_level, list_of_deltas, True, False)
                if enable_memory_tracing:
                    mem_usage = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                cumulative_time = delta_table_exact[-1][3]
                sxs_csv_row_data[3] = cumulative_time
                if enable_memory_tracing:
                    sxs_csv_row_data[21] =  max(mem_usage)

            if exe_kavr: #2024 KAVR
                sxs_kavr = KAVR.Kavr2018(
                avr_task_instance,kavr_precision,kavr_store_demand,print_level)
                delta_table_kavr = [[]]
                if enable_memory_tracing:
                    tracemalloc.start()
                delta_table_kavr = sxs_kavr.calculate_exact_demand(list_of_deltas)
                if enable_memory_tracing:
                    mem_usage = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                cumulative_time = delta_table_kavr[-1][3]
                sxs_csv_row_data[2] = cumulative_time
                if enable_memory_tracing:
                    sxs_csv_row_data[20] =  max(mem_usage)

            if exe_drt == 0: #DRT

                pass


            if create_individual_task_files:
                #Printing First Row of individual \delta file
                sxs_csv_output_data = [-1]*16

                sxs_csv_output_data[0] = "\\delta"
                sxs_csv_output_data[1] = "DRT Demand Calc"
                sxs_csv_output_data[2] = "DRT Single Time"
                sxs_csv_output_data[3] = "DRT Total Time"
                sxs_csv_output_data[4] = "KAVR Demand Calc"
                sxs_csv_output_data[5] = "KAVR Single Time"
                sxs_csv_output_data[6] = "KAVR Total Time"
                sxs_csv_output_data[7] = "KAVR=EXT"
                sxs_csv_output_data[8] = "EXT Demand Calc"
                sxs_csv_output_data[9] = "EXT Single Time"
                sxs_csv_output_data[10] = "EXT Total Time"
                sxs_csv_output_data[11] = "APX Demand Calc"
                sxs_csv_output_data[12] = "APX Single Time"
                sxs_csv_output_data[13] = "APX Total Time"
                sxs_csv_output_data[14] = "APX/KAVR Demand"
                sxs_csv_output_data[15] = "APX/EXT Demand"
                num_data_points = len(sxs_csv_output_data)
                sxs_csv_output_string = ""

                for i in range(num_data_points):
                    sxs_csv_output_string += str(sxs_csv_output_data[i])
                    if i+1 < num_data_points:
                        sxs_csv_output_string += ","
                sxs_csv_output_string += "," + "Log Time\n"
                csv_file.write(sxs_csv_output_string)
                csv_file.flush()

                #Printing data for of individual \delta file
                for i in range(num_deltas):
                    sxs_csv_output_data = [-1]*16
                    sxs_csv_output_data[0] = list_of_deltas[i]

                    if exe_drt :
                        pass

                    if exe_kavr :
                        sxs_csv_output_data[4] = delta_table_kavr[i][1]
                        sxs_csv_output_data[5] = delta_table_kavr[i][2]
                        sxs_csv_output_data[6] = delta_table_kavr[i][3]

                    match = 0
                    if exe_exact and exe_kavr:
                        d_kavr = delta_table_kavr[i][1]
                        d_ext = delta_table_exact[i][1]
                        if int(d_kavr) == 0 and int(d_ext) == -1:
                            match = True
                        else:
                            match = d_ext == d_kavr

                    if exe_exact :
                        sxs_csv_output_data[7] = match
                        sxs_csv_output_data[8] = delta_table_exact[i][1]
                        sxs_csv_output_data[9] = delta_table_exact[i][2]
                        sxs_csv_output_data[10] = delta_table_exact[i][3]

                    if exe_apx :
                        sxs_csv_output_data[11] = delta_table_approximate[i][1]
                        sxs_csv_output_data[12] = delta_table_approximate[i][2]
                        sxs_csv_output_data[13] = delta_table_approximate[i][3]

                    if exe_apx and exe_kavr:
                        d_kavr = delta_table_kavr[i][1]
                        if d_kavr > 0:
                            sxs_csv_output_data[14] = round(
                                delta_table_approximate[i][1]/delta_table_kavr[i][1],AR_ROUND_PREC)
                        else:
                            sxs_csv_output_data[14] = 1
                    else:
                        sxs_csv_output_data[14] = 1

                    if exe_apx and exe_exact:
                        d_ext = delta_table_exact[i][1]
                        if d_ext > 0:
                            sxs_csv_output_data[15] = round(
                                delta_table_approximate[i][1]/delta_table_exact[i][1],AR_ROUND_PREC)
                        else:
                            sxs_csv_output_data[15] = 1
                    else:
                        sxs_csv_output_data[15] = 1

                    num_data_points = len(sxs_csv_output_data)
                    sxs_csv_output_string = ""
                    for j in range(num_data_points):
                        sxs_csv_output_string += str(sxs_csv_output_data[j])
                        if j+1 < num_data_points:
                            sxs_csv_output_string += ","
                    now = datetime.datetime.now()
                    current_time = now.strftime("%H-%M-%S")
                    sxs_csv_output_string += "," + str(current_time) + "\n"
                    csv_file.write(sxs_csv_output_string)
                    csv_file.flush()

                csv_file.close() #Close individual \delta file

            if single_file_for_random_tests:

                #Printing data for of individual \delta file
                for i in range(num_deltas):
                    sxs_csv_output_data = [-1]*22
                    sxs_csv_output_data[0] = list_of_deltas[i]

                    if exe_drt :
                        pass

                    if exe_kavr :
                        sxs_csv_output_data[4] = delta_table_kavr[i][1]
                        sxs_csv_output_data[5] = delta_table_kavr[i][2]
                        sxs_csv_output_data[6] = delta_table_kavr[i][3]

                    match = 0
                    if exe_exact and exe_kavr:
                        d_kavr = delta_table_kavr[i][1]
                        d_ext = delta_table_exact[i][1]
                        if int(d_kavr) == 0 and int(d_ext) == -1:
                            match = True
                        else:
                            match = d_ext == d_kavr

                    if exe_exact :
                        sxs_csv_output_data[7] = match
                        sxs_csv_output_data[8] = delta_table_exact[i][1]
                        sxs_csv_output_data[9] = delta_table_exact[i][2]
                        sxs_csv_output_data[10] = delta_table_exact[i][3]

                    if exe_apx :
                        sxs_csv_output_data[11] = delta_table_approximate[i][1]
                        sxs_csv_output_data[12] = delta_table_approximate[i][2]
                        sxs_csv_output_data[13] = delta_table_approximate[i][3]

                    if exe_apx and exe_kavr:
                        d_kavr = delta_table_kavr[i][1]
                        if d_kavr > 0:
                            sxs_csv_output_data[14] = round(
                                delta_table_approximate[i][1]/delta_table_kavr[i][1],AR_ROUND_PREC)
                        else:
                            sxs_csv_output_data[14] = 1
                    else:
                        sxs_csv_output_data[14] = 1

                    if exe_apx and exe_exact:
                        d_ext = delta_table_exact[i][1]
                        if d_ext > 0:
                            sxs_csv_output_data[15] = round(
                                delta_table_approximate[i][1]/delta_table_exact[i][1],AR_ROUND_PREC)
                        else:
                            sxs_csv_output_data[15] = 1
                    else:
                        sxs_csv_output_data[15] = 1

                    sxs_csv_output_data[16] =  current_sxs_task.apx_obj_instance.epsilon_r
                    sxs_csv_output_data[17] =  current_sxs_task.apx_obj_instance.epsilon_b
                    sxs_csv_output_data[18] =  current_sxs_task.apx_obj_instance.epsilon_f
                    sxs_csv_output_data[19] =  current_sxs_task.apx_obj_instance.one_minus_epsilon
                    sxs_csv_output_data[20] =  current_sxs_task.apx_obj_instance.solution_multiplier

                    sxs_csv_output_data[21] =  current_sxs_task.method_set[1]

                    num_data_points = len(sxs_csv_output_data)
                    sxs_csv_output_string = ""
                    for j in range(num_data_points):
                        sxs_csv_output_string += str(sxs_csv_output_data[j])
                        if j+1 < num_data_points:
                            sxs_csv_output_string += ","
                    now = datetime.datetime.now()
                    current_time = now.strftime("%H-%M-%S")
                    sxs_csv_output_string += "," + str(current_time) + "\n"
                    csv_file_combined.write(sxs_csv_output_string)
                    csv_file_combined.flush()

            if create_sxs_task_file:
                #Printing row for overall sxs file
                sxs_csv_output_string = ""
                num_data_points = len(sxs_csv_row_data)
                for i in range(num_data_points):
                    sxs_csv_output_string += str(sxs_csv_row_data[i])
                    if i+1 < num_data_points:
                        sxs_csv_output_string += ","
                sxs_csv_output_string += "\n"
                csv_file_sxs_tasks_all.write(sxs_csv_output_string)
                csv_file_sxs_tasks_all.flush()

            self.tasks_run += 1

        return 0
