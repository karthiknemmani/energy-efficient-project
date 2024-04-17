class L1Cache:
    """
    L1 Cache, stores data and instructions. 32 KB capacity for each.
    """
    
    def __init__(self):
        # storage containers
        self.data = {}
        self.instructions = {}
        
        # 32 kb size
        self.size = 1 << 15
        
        # access time for reads/writes
        self.access_time = 0.5
        
        # consumption in watts
        self.idle_consumption = 0.5
        self.active_consumption = 1.0   # during reads/writes
        
        # reports
        self.hits = 0
        self.misses = 0
        self.energy = 0.0
        
    def read(self, address):
        """
        Read from cache.
        """
        if address in self.data:
            self.hits += 1
            self.energy += self.active_consumption
            return self.data[address]
        else:
            self.misses += 1
            self.energy += self.active_consumption
            return None
        
        
        
        
        