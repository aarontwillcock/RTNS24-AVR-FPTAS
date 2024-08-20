"""
PDS BPCKP Experiment
"""

from sxs_fxns import exp_runner
from sxs_fxns import exp_task
from sxs_fxns import avr_alg_params
from sxs_fxns import delta_set
from apx_fxns import apx_obj

from avr_fxns import avr_task

#Create algorithm parameters
PRECISION = 12
MEMOIZE = True
GIVE_SLN_SEQ = True
TRACE_MEMORY = False
APX_PARAMS = apx_obj.ApxObj(0.025,0.025,0.025)

#Create task set
omegas = [50, 100, 3200]
wcets = [0, 90000, 600]
MAX_ACCEL = 600000
MODES = len(omegas)-1
custom_task = avr_task.AvrTask(MODES,omegas,wcets,MAX_ACCEL,"oe_example")

#Create delta set
START_DELTA_US = 10000
INCREMENT_DELTA_US = 10000
END_DELTA_US = 2000000
alg_delta_set = delta_set.DeltaSet([0],"oe_example")
alg_delta_set.update_delta_set_with_range(START_DELTA_US,INCREMENT_DELTA_US,END_DELTA_US)

#Set verbosity
VERBOSE = 0

alg_params = avr_alg_params.AvrAlgParams(PRECISION,MEMOIZE,GIVE_SLN_SEQ,TRACE_MEMORY,APX_PARAMS)

custom_experiment = exp_task.ExperimentTask("kavr24",alg_params,custom_task,alg_delta_set,VERBOSE)

exp_runner_instance = exp_runner.ExperimentRunner()

MAKE_DBF_LOG_FILE = False
MAKE_EXP_LOG_FILE = False
MAKE_AGG_LOG_FILE = True

exp_runner_instance.run_experiments([custom_experiment],MAKE_DBF_LOG_FILE,MAKE_EXP_LOG_FILE,MAKE_AGG_LOG_FILE,"oe_example",VERBOSE)
