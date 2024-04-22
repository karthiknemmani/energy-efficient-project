import sys
from Cache import MemorySystem, Cache, DRAM
from collections import Counter

# 015.doduc and 026.compress getting type error
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
        
        self.name = filename.strip('./Traces/Spec_Benchmark/')
        
        with open(filename, 'r') as f:
            assert f.name.endswith('.din'), "File must be of type .din"
            self.data = f.readlines()
        
        # caches
        self.l1_data = Cache(
            block_size=64,
            associativity=1,
            capacity=1 << 15,
            access_time=5e-10,
            idle_consumption=0.5,
            active_consumption=1,
            transfer_penalty=0,
            lower_access_time=0,
            lower_transfer_penalty=0
        )
        self.l1_instruction = Cache(
            block_size=64,
            associativity=1,
            capacity=1 << 15,
            access_time=5e-10,
            idle_consumption=0.5,
            active_consumption=1,
            transfer_penalty=0,
            lower_access_time=0,
            lower_transfer_penalty=0
        )
        self.l2 = Cache(
            block_size=64,
            associativity=4,
            capacity=1 << 18,
            access_time=5e-9,
            idle_consumption=0.8,
            active_consumption=2,
            transfer_penalty=5e-12,
            lower_access_time=5e-10,
            lower_transfer_penalty=0
        )
        
        self.dram = DRAM()
        

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
            value = int(cols[2], 16)
            
            return type_, address, value
        
        for i, line in enumerate(self.data):
            type_, address, value = parse_line(line)
            
            # access the data and handle misses accordingly
            if type_ in (0, 1):
                l1_hit, l1_dirty, evicted_address, evicted_index = \
                    self.l1_data.access(type_, address)
            else:
                l1_hit, l1_dirty, evicted_address, evicted_index = \
                    self.l1_instruction.access(type_, address)

            if not l1_hit:
                if l1_dirty:
                    # writeback to L2
                    self.l2.writeback(evicted_address)
                
                l2_hit, l2_dirty, evicted_address, evicted_index = self.l2.access(type_, address)
                
                if l2_hit:
                    # bring into L1
                    if type_ in (0, 1):
                        self.l1_data.cache_fill(address, evicted_index)
                    else:
                        self.l1_instruction.cache_fill(address, evicted_index)
                else:
                    if l2_dirty:
                        self.dram.writeback()
                        
                    self.dram.access()
                    
                    self.l2.cache_fill(address, evicted_index)
                    if type_ in (0, 1):
                        self.l1_data.cache_fill(address, 0)
                    else:
                        self.l1_instruction.cache_fill(address, 0)
                    
                           
                
    def mem_energy(self, memory: MemorySystem):
        idle_energy = memory.idle_watts() * self.total_time()
        active_energy = memory.active_energy()
        return idle_energy + active_energy
    
    def total_time(self):
        return self.l1_data.total_time() + self.l1_instruction.total_time() + \
            self.l2.total_time() + self.dram.total_time()
    
    def total_energy(self):
        return self.mem_energy(self.l1_data) + self.mem_energy(self.l1_instruction) + \
            self.mem_energy(self.l2) + self.mem_energy(self.dram)
    
    def total_accesses(self):
        return self.l1_data.get_accesses() + self.l1_instruction.get_accesses() + \
            self.l2.get_accesses() + self.dram.get_accesses()
        
    def report(self):
        """
        Output hits, misses, energy consumption, and access time.
        """
        print("__________________________\n")
        # add units later
        print("Cache Access Stats for {}\n".format(self.name))

        print("Hits in L1 Data:", self.l1_data.get_hits())
        print("Misses in L1 Data:", self.l1_data.get_misses())
        print("L1 Data Hit Rate: {:.4f}\n".format(self.l1_data.get_hits() / self.l1_data.get_accesses() if self.l1_data.get_accesses() > 0 else 0))

        print("Hits in L1 Instruction:", self.l1_instruction.get_hits())
        print("Misses in L1 Instruction:", self.l1_instruction.get_misses())
        print("L1 Instruction Hit Rate: {:.4f}\n".format(self.l1_instruction.get_hits() / self.l1_instruction.get_accesses() if self.l1_instruction.get_accesses() > 0 else 0))
        
        print("Hits in L2:", self.l2.get_hits())
        print("Misses in L2:", self.l2.get_misses())
        print("L2 Hit Rate: {:.4f}\n".format(self.l2.get_hits() / self.l2.get_accesses() if self.l2.get_accesses() > 0 else 0))
        
        print(f"DRAM Accesses: {self.dram.get_accesses()}\n")
        
        print("Performance Stats\n")

        print("Energy Consumption from L1: {:.3f} nJ".format((self.mem_energy(self.l1_data) + self.mem_energy(self.l1_instruction)) * 10 ** 9))
        print("Energy Consumption from L2: {:.3f} nJ".format(self.mem_energy(self.l2) * 10 ** 9))
        print("Energy Consumption from DRAM: {:.3f} nJ\n".format(self.mem_energy(self.dram) * 10 ** 9))
        
        print("Total Energy Consumption: {:.3f} nJ\n".format(self.total_energy() * 10 ** 9))
        
        print("Total Time: {:.3f} ns".format(self.total_time() * 10 ** 9))
        print("Average Memory Access Time: {:.3f} ns\n".format((self.total_time() * 10 ** 9) / self.total_accesses()))
        
        # print(Counter(self.l1_data.valid))
        # print(Counter(self.l1_instruction.valid))
        # print(Counter(self.l2.valid))
    

def main():
    # Assert that we have an input file
    if len(sys.argv) != 2:
        print("Usage: python CacheSim.py <input_file>")
        print("File must be a .din file")
        sys.exit(1)
    
    filename = "./Traces/Spec_Benchmark/" + sys.argv[1]
    
    simulator = CacheSim(filename)
    simulator.run()
    simulator.report()

if __name__ == "__main__":
    main()