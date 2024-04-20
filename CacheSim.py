import sys
from Cache import Cache

class CacheSim:
    """
    A Dinero-based cache simulator.
    """
    def __init__(self, filename: str):
        """
        Open the Dinero trace file and initialize simulation statistics.

        Args:
            filename (_str_): The name of the Dinero trace file.
        """
        
        self.name = filename.strip('din')
        
        with open(filename, 'r') as f:
            assert f.name.endswith('.din'), "File must be of type .din"
            self.data = f.readlines()
        
        # caches
        self.l1_data = Cache(64, 1, 1 << 15, 5e-10, 0.5, 1, 0)
        self.l1_instruction = Cache(64, 1, 1 << 15, 5e-10, 0.5, 1, 0)
        self.l2 = Cache(16, 4, 1 << 18, 5e-9, 0.8, 2, 5e-12)
        
        # dram data
        self.dram_access = 5e-8         # in seconds
        self.dram_idle = 0.8            # in watts
        self.dram_active = 4            # in watts
        self.dram_transfer = 6.4e-10    # in joules
        
        # cache stats
        self.l1_hits = 0
        self.l1_misses = 0
        self.l2_hits = 0
        self.l2_misses = 0
        
        # performance data
        self.l1_energy = 0
        self.l2_energy = 0
        self.access_time = 0

    def run(self):
        """
        Run the cache simulator.
        """
        def parse_line(line: str):
            cols = line.split()
            
            assert len(cols) == 3, "Invalid input file format"
            
            # Parse
            type_ = int(cols[0])
            address = int(cols[1], 16)
            value = int(cols[2])
            
            return type_, address, value
        
        for line in self.data:
            type_, address, value = parse_line(line)
            
            # access the data and handle misses accordingly
            l1_hit, l1_dirty = self.l1_data.access(type_, address) \
                if type_ in (0, 1) else \
                self.l1_instruction.access(type_, address)
            
            if l1_hit:
                self.l1_hits += 1
                
                # implement eviction if needed
            else:
                self.l1_misses += 1
                l2_hit, l2_dirty = self.l2.access(type_, address)
                if l2_hit:
                    self.l2_hits += 1
                    # implement eviction if needed
                else:
                    self.l2_misses += 1
                    # implement DRAM access
            
            # update hits, misses, energy, access time

    def report(self):
        """
        Output hits, misses, energy consumption, and access time.
        """
        
        # add units later
        print("Cache Access Stats for {}".format(self.name))
        print("__________________________\n")
        
        print("Hits in L1:", self.l1_hits)
        print("Misses in L1:", self.l1_misses)
        
        total = self.l1_hits + self.l1_misses
        miss_rate = self.l1_misses / total if total > 0 else 0
        
        print("L1 Miss Rate: %0.4f\n".format(miss_rate))
        
        print("Hits in L2:", self.l2_hits)
        print("Misses in L2:", self.l2_misses)
        print("L2 Miss Rate: %0.4f\n".format(self.l2_misses / 
                                           (self.l2_hits + self.l2_misses)))
        
        print("Performance Stats")
        print("__________________________\n")
        
        print("Energy Consumption from L1: %0.4f".format(self.l1_energy))
        print("Energy Consumption from L2: %0.4f\n".format(self.l2_energy))
        
        print("Average Memory Access Time: %0.4f".format(self.access_time / len(self.data)))
        
    

def main():
    # Assert that we have an input file
    if len(sys.argv) != 2:
        print("Usage: python CacheSim.py <input_file>")
        print("File must be a .din file")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    simulator = CacheSim(filename)
    simulator.run()
    simulator.report()

if __name__ == "__main__":
    main()