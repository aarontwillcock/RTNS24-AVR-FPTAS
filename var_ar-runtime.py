"""
PDS BPCKP Experiment
"""

from sxs_fxns import exp_runner
from sxs_fxns import exp_task
from sxs_fxns import avr_alg_params
from sxs_fxns import delta_set
from task_sets import lit_avr_task_sets
from apx_fxns import apx_obj

#pylint: disable=C0200,C0301

EXPERIMENT_NAME = "var_ar-runtime"

#Create algorithm parameters
PRECISION12 = 12
MEMOIZE = True
GIVE_SLN_SEQ = False
TRACE_MEMORY = False
APX_PARAMS = apx_obj.ApxObj(0.025,0.025,0.025)

delta_times_us = [1000000]
alg_delta_set = delta_set.DeltaSet(delta_times_us,"1s")

#Verbosity
VERBOSE = 0

#Create task set
lit_task_set = lit_avr_task_sets.LitAvrTaskSets()
task_set_can = lit_task_set.avr_task_instance_2018_existing
task_set_gen = lit_task_set.avr_task_instance_2018_general

#Create approximation parameters set
APX_PARAM_SET_LEN = 13
APX_PARAM_SET = [-1]*APX_PARAM_SET_LEN
APX_PARAM_SET[0] = apx_obj.ApxObj(0.1, 0.1, 0.1)

for i in range(4):
    APX_PARAM_SET[1+i] = apx_obj.ApxObj(0.02*(i+1), 0.1, 0.1)

for i in range(4):
    APX_PARAM_SET[5+i] = apx_obj.ApxObj(0.1, 0.02*(i+1), 0.1)

for i in range(4):
    APX_PARAM_SET[9+i] = apx_obj.ApxObj(0.1, 0.1, 0.02*(i+1))

alg_params_p12_set = [-1]*APX_PARAM_SET_LEN
var_apx_ratio_sln_qual_apx_can_set = [-1]*APX_PARAM_SET_LEN
var_apx_ratio_sln_qual_apx_gen_set = [-1]*APX_PARAM_SET_LEN
for i in range(APX_PARAM_SET_LEN):
    alg_params_p12_set[i] = avr_alg_params.AvrAlgParams(PRECISION12,MEMOIZE,GIVE_SLN_SEQ,TRACE_MEMORY,APX_PARAM_SET[i])
    var_apx_ratio_sln_qual_apx_can_set[i] = exp_task.ExperimentTask("apx",alg_params_p12_set[i],task_set_can,alg_delta_set,VERBOSE)
    var_apx_ratio_sln_qual_apx_gen_set[i] = exp_task.ExperimentTask("apx",alg_params_p12_set[i],task_set_gen,alg_delta_set,VERBOSE)

exp_runner_instance = exp_runner.ExperimentRunner()

MAKE_DBF_LOG_FILE = False
MAKE_EXP_LOG_FILE = False
MAKE_AGG_LOG_FILE = True

#Execute
exp_runner_instance.run_experiments(var_apx_ratio_sln_qual_apx_can_set,MAKE_DBF_LOG_FILE,MAKE_EXP_LOG_FILE,MAKE_AGG_LOG_FILE,EXPERIMENT_NAME,VERBOSE)
exp_runner_instance.run_experiments(var_apx_ratio_sln_qual_apx_gen_set,MAKE_DBF_LOG_FILE,MAKE_EXP_LOG_FILE,MAKE_AGG_LOG_FILE,EXPERIMENT_NAME,VERBOSE)
