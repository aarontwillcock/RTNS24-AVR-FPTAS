"""AVR Task Demand algorithm parameters"""

class AvrAlgParams:

    """Generic interface for AVR Task Demand algorithm parameters"""

    def __init__(self,precision,memoize,give_sln_seq,trace_memory,apx_params=None):

        self.update_params(precision,memoize,give_sln_seq,trace_memory,apx_params)

    def update_params(self,precision,memoize,give_sln_seq,trace_memory,apx_params):

        """Update algorithm parameters"""

        self.precision = precision
        self.memoize = memoize
        self.give_sln_seq = give_sln_seq
        self.trace_memory = trace_memory
        self.apx_params = apx_params
