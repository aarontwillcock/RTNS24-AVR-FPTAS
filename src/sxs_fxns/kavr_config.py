"""KAVR precision and demand storage config"""

class KavrConfig:

    """KAVR precision and demand storage config"""

    def __init__(self,kavr_precision,kavr_store_demand):

        self.kavr_precision = kavr_precision
        self.kavr_store_demand = kavr_store_demand

    def update_config(self,kavr_precision,kavr_store_demand):

        self.kavr_precision = kavr_precision
        self.kavr_store_demand = kavr_store_demand