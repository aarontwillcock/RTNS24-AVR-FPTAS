"""
PDS BPCKP Experiment
"""

import math

from sxs_fxns import exp_runner
from sxs_fxns import exp_task
from sxs_fxns import avr_alg_params
from sxs_fxns import delta_set
from task_sets import lit_avr_task_sets
from apx_fxns import apx_obj

EXPERIMENT_NAME = "var_duration"


#Create algorithm parameters
PRECISION = 12
MEMOIZE = True
GIVE_SLN_SEQ = False
TRACE_MEMORY = False
APX_PARAMS = apx_obj.ApxObj(0.025,0.025,0.025)

#Create can task sets
lit_task_set = lit_avr_task_sets.LitAvrTaskSets()
task_set_can = lit_task_set.avr_task_instance_2018_existing
task_set_gen = lit_task_set.avr_task_instance_2018_general


#Create delta set
START_DELTA_US = 10000
POWERS = 4
INDICES = 5

delta_times_us = []

for i in range(POWERS):
    for j in range(INDICES):
        delta_times_us += [START_DELTA_US*int(math.pow(10,i))*(j+1)]

CUTOFF = 17
delta_times_us = delta_times_us[:CUTOFF]
alg_delta_set = delta_set.DeltaSet(delta_times_us,"2.0e7")

#Set verbosity
VERBOSE = 0

alg_params = avr_alg_params.AvrAlgParams(PRECISION,MEMOIZE,GIVE_SLN_SEQ,TRACE_MEMORY,APX_PARAMS)

#Canonical
var_precision_alg_exp_kavr24_p5_can = exp_task.ExperimentTask("kavr24",alg_params,task_set_can,alg_delta_set,VERBOSE)

#General
var_precision_alg_exp_kavr24_p5_gen = exp_task.ExperimentTask("kavr24",alg_params,task_set_gen,alg_delta_set,VERBOSE)

exp_runner_instance = exp_runner.ExperimentRunner()

make_dbf_log_file = False
make_exp_log_file = False
make_agg_log_file = True

#Canonical
exp_runner_instance.run_experiments([var_precision_alg_exp_kavr24_p5_can],make_dbf_log_file,make_exp_log_file,make_agg_log_file,EXPERIMENT_NAME,VERBOSE)

#General
exp_runner_instance.run_experiments([var_precision_alg_exp_kavr24_p5_gen],make_dbf_log_file,make_exp_log_file,make_agg_log_file,EXPERIMENT_NAME,VERBOSE)
