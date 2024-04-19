import sys

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
        def parse_line(line):
            cols = line.split()
            
            # Parse
            type_ = int(cols[0])
            address = int(cols[1], 16)
            size = int(cols[2])
            
            return type_, address, size
        
        for line in self.data:
            type_, address, size = parse_line(line)
            
            # access the data and handle misses accordingly
            
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
        print("L1 Miss Rate: %0.4f\n".format(self.l1_misses / 
                                           (self.l1_hits + self.l1_misses)))
        
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
        sys.exit(1)
    
    filename = sys.argv[1]
    
    simulator = CacheSim(filename)
    simulator.run()
    simulator.report()

if __name__ == "__main__":
    main()