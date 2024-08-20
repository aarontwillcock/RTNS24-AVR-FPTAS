"""Module for creating output file names"""

def create_output_filename(experiment_name,task_set,method_set,kavr_config,memory_tracing):

    """Create output filename using experiment name, task set, method set, kavr config, and memory tracing params"""

    experiment_name = experiment_name + "-"
    task_set = task_set + "-"
    algorithms_used = ""
    precision_used = ""
    memoization_used = ""
    memory_tracing_used = ""

    kavr_precision = kavr_config.kavr_precision
    kavr_store_demand = kavr_config.kavr_store_demand

    #Algorithms
    if method_set[0]:
        algorithms_used += "row17-"
    if method_set[1]:
        algorithms_used += "kavr24-"
    if method_set[2]:
        algorithms_used += "exact-"
    if method_set[3]:
        algorithms_used += "apx-"

    #Precision
    if method_set[1]:
        precision_used += "p"+str(kavr_precision) + "-"

    #Memoization
    if method_set[1]:
        if kavr_store_demand:
            memoization_used += "memo-1-"
        else:
            memoization_used += "memo-0-"

    #Memory Tracing
    if memory_tracing:
        memory_tracing_used += "trace-1"
    else:
        memory_tracing_used += "trace-0"

    output_filename = experiment_name+task_set+algorithms_used+precision_used+memoization_used+memory_tracing_used

    return output_filename