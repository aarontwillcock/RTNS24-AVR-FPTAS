"""
PDS BPCKP Experiment
"""

from sxs_fxns import exp_runner
from sxs_fxns import exp_task
from sxs_fxns import avr_alg_params
from sxs_fxns import delta_set
from task_sets import lit_avr_task_sets
from apx_fxns import apx_obj

#Create algorithm parameters
PRECISION = 12
MEMOIZE = True
GIVE_SLN_SEQ = False
TRACE_MEMORY = False
APX_PARAMS = apx_obj.ApxObj(0.025,0.025,0.025)

#Create task set
lit_task_set = lit_avr_task_sets.LitAvrTaskSets()
task_set_can = lit_task_set.avr_task_instance_2018_existing
task_set_gen = lit_task_set.avr_task_instance_2018_general

#Create delta set
START_DELTA_US = 10000
INCREMENT_DELTA_US = 1000
END_DELTA_US = 500000
alg_delta_set = delta_set.DeltaSet([0],"high_gran")
alg_delta_set.update_delta_set_with_range(START_DELTA_US,INCREMENT_DELTA_US,END_DELTA_US)

#Set verbosity
VERBOSE = 0

alg_params = avr_alg_params.AvrAlgParams(PRECISION,MEMOIZE,GIVE_SLN_SEQ,TRACE_MEMORY,APX_PARAMS)

var_precision_alg_exp_kavr24_can = exp_task.ExperimentTask("kavr24",alg_params,task_set_can,alg_delta_set,VERBOSE)
var_precision_alg_exp_kavr24_gen = exp_task.ExperimentTask("kavr24",alg_params,task_set_gen,alg_delta_set,VERBOSE)

exp_runner_instance = exp_runner.ExperimentRunner()

MAKE_DBF_LOG_FILE = False
MAKE_EXP_LOG_FILE = False
MAKE_AGG_LOG_FILE = True

exp_runner_instance.run_experiments([var_precision_alg_exp_kavr24_can],MAKE_DBF_LOG_FILE,MAKE_EXP_LOG_FILE,MAKE_AGG_LOG_FILE,"var_precision_hg",VERBOSE)
exp_runner_instance.run_experiments([var_precision_alg_exp_kavr24_gen],MAKE_DBF_LOG_FILE,MAKE_EXP_LOG_FILE,MAKE_AGG_LOG_FILE,"var_precision_hg",VERBOSE)
