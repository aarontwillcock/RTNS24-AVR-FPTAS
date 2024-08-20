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

#pylint: disable=C0200,C0301

EXPERIMENT_NAME = "var_accel"


#Create algorithm parameters
PRECISION = 5
MEMOIZE = True
GIVE_SLN_SEQ = False
TRACE_MEMORY = False
APX_PARAMS = apx_obj.ApxObj(0.025,0.025,0.025)

#Create can task sets
lit_task_set = lit_avr_task_sets.LitAvrTaskSets()
task_set_can = lit_task_set.avr_task_instance_2018_existing
task_set_gen = lit_task_set.avr_task_instance_2018_general


#Create accel set
BASE_ACCELERATION = 10000
ACCEL_SET = []
for i in range(100):
    ACCEL_SET += [BASE_ACCELERATION*(i+1)]

delta_times_us = [1000000]
alg_delta_set = delta_set.DeltaSet(delta_times_us,"1s")

#Set verbosity
VERBOSE = 0

PRECISION12 = 12

PRECISION5 = 5

alg_params_p5 = avr_alg_params.AvrAlgParams(PRECISION5,MEMOIZE,GIVE_SLN_SEQ,TRACE_MEMORY,APX_PARAMS)
alg_params_p12 = avr_alg_params.AvrAlgParams(PRECISION12,MEMOIZE,GIVE_SLN_SEQ,TRACE_MEMORY,APX_PARAMS)

#Canonical
var_precision_alg_exp_row17_p5_can_set = [-1]*len(ACCEL_SET)
var_precision_alg_exp_kavr18_p5_can_set = [-1]*len(ACCEL_SET)
var_precision_alg_exp_kavr24_p5_can_set = [-1]*len(ACCEL_SET)
var_precision_alg_exp_exact_can_set = [-1]*len(ACCEL_SET)
var_precision_alg_exp_apx_can_set = [-1]*len(ACCEL_SET)

for i in range(len(ACCEL_SET)):
    var_precision_alg_exp_row17_p5_can_set[i] = exp_task.ExperimentTask("row17",alg_params_p5,task_set_can,alg_delta_set,VERBOSE)
    var_precision_alg_exp_kavr18_p5_can_set[i] = exp_task.ExperimentTask("kavr18",alg_params_p5,task_set_can,alg_delta_set,VERBOSE)
    var_precision_alg_exp_kavr24_p5_can_set[i] = exp_task.ExperimentTask("kavr24",alg_params_p5,task_set_can,alg_delta_set,VERBOSE)
    var_precision_alg_exp_exact_can_set[i] = exp_task.ExperimentTask("exact",alg_params_p12,task_set_can,alg_delta_set,VERBOSE)
    var_precision_alg_exp_apx_can_set[i] = exp_task.ExperimentTask("apx",alg_params_p12,task_set_can,alg_delta_set,VERBOSE)

    var_precision_alg_exp_row17_p5_can_set[i].avr_task_instance.alpha = ACCEL_SET[i]
    var_precision_alg_exp_kavr18_p5_can_set[i].avr_task_instance.alpha = ACCEL_SET[i]
    var_precision_alg_exp_kavr24_p5_can_set[i].avr_task_instance.alpha = ACCEL_SET[i]
    var_precision_alg_exp_exact_can_set[i].avr_task_instance.alpha = ACCEL_SET[i]
    var_precision_alg_exp_apx_can_set[i].avr_task_instance.alpha = ACCEL_SET[i]

#General
var_precision_alg_exp_row17_p5_gen_set = [-1]*len(ACCEL_SET)
var_precision_alg_exp_kavr18_p5_gen_set = [-1]*len(ACCEL_SET)
var_precision_alg_exp_kavr24_p5_gen_set = [-1]*len(ACCEL_SET)
var_precision_alg_exp_exact_gen_set = [-1]*len(ACCEL_SET)
var_precision_alg_exp_apx_gen_set = [-1]*len(ACCEL_SET)

for i in range(len(ACCEL_SET)):
    var_precision_alg_exp_row17_p5_gen_set[i] = exp_task.ExperimentTask("row17",alg_params_p5,task_set_gen,alg_delta_set,VERBOSE)
    var_precision_alg_exp_kavr18_p5_gen_set[i] = exp_task.ExperimentTask("kavr18",alg_params_p5,task_set_gen,alg_delta_set,VERBOSE)
    var_precision_alg_exp_kavr24_p5_gen_set[i] = exp_task.ExperimentTask("kavr24",alg_params_p5,task_set_gen,alg_delta_set,VERBOSE)
    var_precision_alg_exp_exact_gen_set[i] = exp_task.ExperimentTask("exact",alg_params_p12,task_set_gen,alg_delta_set,VERBOSE)
    var_precision_alg_exp_apx_gen_set[i] = exp_task.ExperimentTask("apx",alg_params_p12,task_set_gen,alg_delta_set,VERBOSE)

    var_precision_alg_exp_row17_p5_gen_set[i].avr_task_instance.alpha = ACCEL_SET[i]
    var_precision_alg_exp_kavr18_p5_gen_set[i].avr_task_instance.alpha = ACCEL_SET[i]
    var_precision_alg_exp_kavr24_p5_gen_set[i].avr_task_instance.alpha = ACCEL_SET[i]
    var_precision_alg_exp_exact_gen_set[i].avr_task_instance.alpha = ACCEL_SET[i]
    var_precision_alg_exp_apx_gen_set[i].avr_task_instance.alpha = ACCEL_SET[i]

exp_runner_instance = exp_runner.ExperimentRunner()

MAKE_DBF_LOG_FILE = False
MAKE_EXP_LOG_FILE = False
MAKE_AGG_LOG_FILE = True

#Canonical
# exp_runner_instance.run_experiments(var_precision_alg_exp_row17_p5_can_set,MAKE_DBF_LOG_FILE,MAKE_EXP_LOG_FILE,MAKE_AGG_LOG_FILE,EXPERIMENT_NAME,VERBOSE)
exp_runner_instance.run_experiments(var_precision_alg_exp_kavr18_p5_can_set,MAKE_DBF_LOG_FILE,MAKE_EXP_LOG_FILE,MAKE_AGG_LOG_FILE,EXPERIMENT_NAME,VERBOSE)
# exp_runner_instance.run_experiments(var_precision_alg_exp_kavr24_p5_can_set,MAKE_DBF_LOG_FILE,MAKE_EXP_LOG_FILE,MAKE_AGG_LOG_FILE,EXPERIMENT_NAME,VERBOSE)
# exp_runner_instance.run_experiments(var_precision_alg_exp_exact_can_set,MAKE_DBF_LOG_FILE,MAKE_EXP_LOG_FILE,MAKE_AGG_LOG_FILE,EXPERIMENT_NAME,VERBOSE)
# exp_runner_instance.run_experiments(var_precision_alg_exp_apx_can_set,MAKE_DBF_LOG_FILE,MAKE_EXP_LOG_FILE,MAKE_AGG_LOG_FILE,EXPERIMENT_NAME,VERBOSE)

#General
# exp_runner_instance.run_experiments(var_precision_alg_exp_row17_p5_gen_set,MAKE_DBF_LOG_FILE,MAKE_EXP_LOG_FILE,MAKE_AGG_LOG_FILE,EXPERIMENT_NAME,VERBOSE)
exp_runner_instance.run_experiments(var_precision_alg_exp_kavr18_p5_gen_set,MAKE_DBF_LOG_FILE,MAKE_EXP_LOG_FILE,MAKE_AGG_LOG_FILE,EXPERIMENT_NAME,VERBOSE)
# exp_runner_instance.run_experiments(var_precision_alg_exp_kavr24_p5_gen_set,MAKE_DBF_LOG_FILE,MAKE_EXP_LOG_FILE,MAKE_AGG_LOG_FILE,EXPERIMENT_NAME,VERBOSE)
# exp_runner_instance.run_experiments(var_precision_alg_exp_exact_gen_set,MAKE_DBF_LOG_FILE,MAKE_EXP_LOG_FILE,MAKE_AGG_LOG_FILE,EXPERIMENT_NAME,VERBOSE)
# exp_runner_instance.run_experiments(var_precision_alg_exp_apx_gen_set,MAKE_DBF_LOG_FILE,MAKE_EXP_LOG_FILE,MAKE_AGG_LOG_FILE,EXPERIMENT_NAME,VERBOSE)
