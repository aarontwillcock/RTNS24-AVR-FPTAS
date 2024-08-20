"""
PDS BPCKP Experiment
"""

import copy
import math
from apx_fxns import apx_obj
from sxs_fxns import sxs_task
from sxs_fxns import kavr_config
from sxs_fxns import sxs_runner
from sxs_fxns import delta_set
from task_sets import mode_16_model as MODE16_EXP
from output_file_name_gen import sxs_output_fn_gen

mode16_exp_instance = MODE16_EXP.UserTaskSet()

EXPERIMENT_NAME = "var_mode_16"

START_TIME = 750000
INCREMENT_TIME = 10000
MAX_TIME = 750000
UNITS_PER_US = 1
var_delta_set = delta_set.DeltaSet(START_TIME, INCREMENT_TIME, MAX_TIME, UNITS_PER_US)
apx_obj_instance = apx_obj.ApxObj(0.025, 0.025, 0.025)
kavr_config = kavr_config.KavrConfig(5,True)
PRINT_CONFIG = 2

method_set = [False,True,False,True] #DRT,KAVR,EXACT,APX
avr_task_instances = [0]*15
avr_task_instances[0] = copy.deepcopy(mode16_exp_instance.avr_task_instance_user_task_set)

for i in range(16-2):
    index = i+1
    avr_task_instances[index] = copy.deepcopy(avr_task_instances[index-1])
    #delete middle WCET
    avr_task_instances[index].wcet = copy.deepcopy(avr_task_instances[index].wcet)
    length = len(avr_task_instances[index].wcet)
    middle_index = length//2
    avr_task_instances[index].wcet.remove(avr_task_instances[index].wcet[middle_index])
    #delete middle omega
    avr_task_instances[index].omega = copy.deepcopy(avr_task_instances[index].omega)
    avr_task_instances[index].omega.remove(avr_task_instances[index].omega[middle_index])
    #reduce m by one
    avr_task_instances[index].m = copy.deepcopy(avr_task_instances[index].m-1)

sxs_task_instances = [0]*15

#SXS Instances
for i in range(16-1):
    sxs_task_instances[i] = sxs_task.SxsTask(avr_task_instances[i], apx_obj_instance, var_delta_set, method_set, kavr_config, PRINT_CONFIG)

sxs_task_instances.reverse()

sxs_tasks = sxs_task_instances
NUM_SXS_TASKS = len(sxs_tasks)

CREATE_INDIVIDUAL_TASK_FILES_VALUE = False
CREATE_SXS_TASK_FILE_VALUE = True
ENABLE_MEMORY_TRACING = False
#Create filename
output_fn = sxs_output_fn_gen.create_output_filename(EXPERIMENT_NAME,
    "rng",method_set,kavr_config,ENABLE_MEMORY_TRACING)
sxs_runner_instance = sxs_runner.SxsRunner(NUM_SXS_TASKS)
sxs_runner_instance.run_tasks_side_by_side(sxs_tasks,
    CREATE_INDIVIDUAL_TASK_FILES_VALUE,
    CREATE_SXS_TASK_FILE_VALUE,
    output_fn,
    True,
    ENABLE_MEMORY_TRACING)
