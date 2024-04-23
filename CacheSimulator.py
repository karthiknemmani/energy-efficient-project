import math
import random
import sys

clock = 0

class L1Cache:
    """
    L1 cache class.
    """
    def __init__(self, l2):
        # constants
        self.access_time = 5e-10
        self.idle_consumption = 0.5
        self.active_consumption = 1
        self.l2 = l2
        
        self.block_size = 64
        self.capacity = 1 << 15
        
        # masking attributes
        sets = self.capacity // self.block_size
        
        self.block_bits = int(math.log2(self.block_size))
        self.set_bits = int(math.log2(sets))
        
        self.set_mask = sets - 1
        self.tag_offset = self.block_bits + self.set_bits
        
        # cache storage container
        self.tags = [-1] * sets
        self.valid = [False] * sets
        
        # computed totals
        self.total_active_energy = 0
        self.accesses = 0
        self.misses = 0

    def get_set(self, address):
        """
        Extract the bits of the address to determine the set index.
        """
        return (address >> self.block_bits) & self.set_mask
    
    def get_tag(self, address):
        """
        Extract the bits of the address to determine the tag.
        """
        tag_size = 32 - (self.block_bits + self.set_bits)
        return (address >> self.tag_offset) & ((1 << tag_size) - 1)
    
    def read(self, address):
        """
        Read a block from the cache. Returns whether or not the block was
        found in the cache.
        """
        global clock
        
        self.accesses += 1
        self.total_active_energy += self.active_consumption * self.access_time
        clock += self.access_time
        
        set_index = self.get_set(address)
        tag = self.get_tag(address)
        
        if self.valid[set_index]:
            if tag == self.tags[set_index]:
                # hit
                return True
            else:
                # eviction
                return self.evict(set_index, tag)
        else:
            # compulsory miss, no eviction
            return self.invalid_miss(set_index, tag)
    
    def write(self, address):
        """
        Write to a block in cache. Returns whether or not the block was
        found in the cache.
        """
        self.accesses += 1
        self.total_active_energy += self.active_consumption * self.access_time
        
        set_index = self.get_set(address)
        tag = self.get_tag(address)
        
        if self.valid[set_index]:
            if tag == self.tags[set_index]:
                # write through to l2
                self.l2.write(address)
                return True
            else:
                # eviction
                self.evict(set_index, tag)
                return False
        else:
            # compulsory miss, no eviction
            self.invalid_miss(set_index, tag)
            return False
    
    def evict(self, set_index, tag):
        """
        Evict a block from the cache. L1 logic is the same as handling
        a compulsory miss due to directly-mapped nature and 
        write-through to L2.
        """
        self.misses += 1   
        self.tags[set_index] = tag
        self.valid[set_index] = True
    
    def invalid_miss(self, set_index, tag):
        """
        Handle a compulsory miss.
        """
        self.misses += 1
        self.tags[set_index] = tag
        self.valid[set_index] = True

    def invalidate(self, address):
        """
        Back-invalidate a block from this cache that was just evicted in L2.
        """
        set_index = self.get_set(address)
        tag = self.get_tag(address)
        
        # check if the block is in the cache
        if self.valid[set_index] and tag == self.tags[set_index]:
            self.valid[set_index] = False
            self.tags[set_index] = -1
    
    def active_energy(self):
        return self.total_active_energy
    
    def idle_energy(self):
        return self.idle_consumption * clock
    
    def get_accesses(self):
        return self.accesses
    
    def get_misses(self):
        return self.misses
    
    def get_hits(self):
        return self.accesses - self.misses
    
    
    
class L2Cache:
    """
    L2 cache class.
    """
    def __init__(self, associativity, l1_data, l1_instr, dram):
        self.access_time = 4.5e-9    # account for additive
        self.idle_consumption = 0.8
        self.active_consumption = 2
        self.transfer_penalty = 5e-12
        
        self.l1_data = l1_data
        self.l1_instr = l1_instr
        self.dram = dram
        
        self.block_size = 64
        self.capacity = 1 << 18
        self.associativity = associativity
        
        sets = self.capacity // (self.block_size * self.associativity)
        
        self.block_bits = int(math.log2(self.block_size))
        self.set_bits = int(math.log2(sets))
        
        self.set_mask = sets - 1
        self.tag_offset = self.block_bits + self.set_bits
        
        self.tags = [[-1] * self.associativity for _ in range(sets)]
        self.valid = [[False] * self.associativity for _ in range(sets)]
        self.dirty = [[False] * self.associativity for _ in range(sets)]
        
        self.total_active_energy = 0
        self.accesses = 0
        self.misses = 0
        
    def get_set(self, address):
        """
        Extract the bits of the address to determine the set index.
        """
        return (address >> self.block_bits) & self.set_mask
    
    def get_tag(self, address):
        """
        Extract the bits of the address to determine the tag.
        """
        tag_size = 32 - (self.block_bits + self.set_bits)
        return (address >> self.tag_offset) & ((1 << tag_size) - 1)
    
    def read(self, address):
        """
        Read a block from cache. Returns whether or not the block was
        found in the cache.
        """
        global clock
        
        self.accesses += 1
        self.total_active_energy += (self.active_consumption * self.access_time + self.transfer_penalty)
        clock += self.access_time
        
        set_index = self.get_set(address)
        tag = self.get_tag(address)
        
        # search through the set for the block
        invalid = -1
        for i in range(len(self.tags[set_index])):
            if self.valid[set_index][i]:
                if tag == self.tags[set_index][i]:
                    # read hit
                    return True
            else:
                # mark an invalid block to fill later
                invalid = i
        
        # we have a miss
        if invalid != -1:
            # we have an invalid block
            self.invalid_miss(set_index, invalid, tag, False)
            return False
        else:
            # eviction
            return self.evict(address, False)
        
    def write(self, address):
        """
        Write to a block in cache. Returns whether or not the block was
        found in the cache.
        """
        
        self.accesses += 1
        self.total_active_energy += (self.active_consumption * self.access_time + self.transfer_penalty)
        
        set_index = self.get_set(address)
        tag = self.get_tag(address)
        
        # search through the set for the block
        invalid = -1
        for i in range(len(self.tags[set_index])):
            if self.valid[set_index][i]:
                if tag == self.tags[set_index][i]:
                    # write hit
                    self.dirty[set_index][i] = True
                    return True
            else:
                # mark an invalid block to fill later
                invalid = i
        
        # we have a miss
        if invalid != -1:
            # we have an invalid block
            self.invalid_miss(set_index, invalid, tag, True)
            return False
        else:
            # eviction
            self.evict(address, True)
            return False
    
    def invalid_miss(self, set_index, index, tag, write):
        """
        Handle a compulsory miss.
        """
        self.misses += 1
        self.tags[set_index][index] = tag
        self.valid[set_index][index] = True
        self.dirty[set_index][index] = write
    
    def evict(self, address, write):
        """
        Evict a random block from a set in the cache.
        """
        self.misses += 1
        
        set_index = self.get_set(address)
        tag = self.get_tag(address)
        
        # randomly select a block to evict
        index = random.randint(0, self.associativity - 1)
        
        # evict from L1 to maintain inclusivity
        self.l1_data.invalidate(address)
        self.l1_instr.invalidate(address)
        
        # write back to dram if evicted block is dirty
        if self.dirty[set_index][index]:
            self.dram.writeback()
            
        self.tags[set_index][index] = tag
        self.valid[set_index][index] = True
        self.dirty[set_index][index] = write
    
    def active_energy(self):
        return self.total_active_energy
    
    def idle_energy(self):
        return self.idle_consumption * clock
    
    def set_l1(self, data, instr):
        self.l1_data = data
        self.l1_instr = instr
    
    def get_accesses(self):
        return self.accesses
    
    def get_misses(self):
        return self.misses
    
    def get_hits(self):
        return self.accesses - self.misses
    
class DRAM:
    def __init__(self):
        self.access_time = 4.5e-8       # account for additive
        self.idle_consumption = 0.8
        self.active_consumption = 4
        self.transfer_penalty = 6.45e-10    # transfer from dram to l1
        
        self.total_active_energy = 0
        self.accesses = 0
    
    def read(self):
        """
        Compute the time and energy for a read from DRAM.
        """
        global clock
        
        self.accesses += 1
        clock += self.access_time
        self.total_active_energy += (self.active_consumption * self.access_time + self.transfer_penalty)
    
    def writeback(self):
        """
        Compute the energy for a writeback to DRAM.
        """
        self.accesses += 1
        self.total_active_energy += (self.active_consumption * self.access_time + self.transfer_penalty)
    
    def active_energy(self):
        return self.total_active_energy
    
    def idle_energy(self):
        return self.idle_consumption * clock
    
    def get_accesses(self):
        return self.accesses
    
class CacheSim:
    """
    A Dinero-based cache simulator.
    """
    def __init__(self, filename: str, l2_assoc: int = 4):
        """
        Open the Dinero trace file and initialize simulation statistics.
        """
        self.name = filename[24:]
        self.l2_assoc = l2_assoc
        
        with open(filename, 'r') as f:
            assert f.name.endswith('.din'), "File must be of type .din"
            self.data = f.readlines()
        
        # caches
        self.dram = DRAM()
        
        self.l2 = L2Cache(
            associativity=self.l2_assoc,
            l1_data=None,
            l1_instr=None,
            dram=self.dram
        )
        
        self.l1_data = L1Cache(self.l2)
        self.l1_instruction = L1Cache(self.l2)
        
        # l2 initialized before l1, so need this
        self.l2.set_l1(self.l1_data, self.l1_instruction)
    
    
    """
    Access methods.
    """

    def read_access(self, address, data=True):
        """
        Perform a read.
        """
        l1_cache = self.l1_data if data else self.l1_instruction
        l1_hit = l1_cache.read(address)
        if not l1_hit:
            l2_hit = self.l2.read(address)
            if not l2_hit:
                self.dram.read()

    def write_access(self, address):
        """
        Perform a write.
        """
        l1_hit = self.l1_data.write(address)
        if not l1_hit:
            self.l2.write(address)
            
    def line_access(self, type_: int, address: int):
        """
        Access an address given by a Dinero line.
        """
        if type_ == 0:
            self.read_access(address, data=True)
        elif type_ == 1:
            self.write_access(address)
        elif type_ == 2:
            self.read_access(address, data=False)
    

    def run(self):
        """
        Run the cache simulator.
        """
        def parse_line(line: str):
            cols = line.split()
            
            assert len(cols) == 3, "Invalid input file format"
            
            # Parse, only need type and address
            type_ = int(cols[0])
            address = int(cols[1], 16)
            
            return type_, address
        
        for line in self.data:
            type_, address = parse_line(line)
            
            # access the data and handle misses accordingly
            self.line_access(type_, address)
        
    def report(self):
        """
        Output hits, misses, energy consumption, and access time.
        """
        # add units later
        print("Cache Access Stats for {}\n".format(self.name))

        print("Hits in L1 Data:", self.l1_data.get_hits())
        print("Misses in L1 Data:", self.l1_data.get_misses())
        print("L1 Data Hit Rate: {:.6f}\n".format(self.l1_data.get_hits() / self.l1_data.get_accesses() if self.l1_data.get_accesses() > 0 else 0))

        print("Hits in L1 Instruction:", self.l1_instruction.get_hits())
        print("Misses in L1 Instruction:", self.l1_instruction.get_misses())
        print("L1 Instruction Hit Rate: {:.6f}\n".format(self.l1_instruction.get_hits() / self.l1_instruction.get_accesses() if self.l1_instruction.get_accesses() > 0 else 0))
        
        print("Hits in L2:", self.l2.get_hits())
        print("Misses in L2:", self.l2.get_misses())
        print("L2 Hit Rate: {:.6f}\n".format(self.l2.get_hits() / self.l2.get_accesses() if self.l2.get_accesses() > 0 else 0))
        
        print(f"DRAM Accesses: {self.dram.get_accesses()}\n")
        
        print("Performance Stats\n")

        print("Idle Consumption from L1 Data: {:.9f} J".format((self.l1_data.idle_energy())))
        print("Active Consumption from L1 Data: {:.9f} J".format((self.l1_data.active_energy())))
        print("Total Consumption from L1 Data: {:.9f} J\n".format(self.l1_data.idle_energy() + self.l1_data.active_energy()))
        
        print("Idle Consumption from L1 Instruction: {:.9f} J".format((self.l1_instruction.idle_energy())))
        print("Active Consumption from L1 Instruction: {:.9f} J".format((self.l1_instruction.active_energy())))
        print("Total Consumption from L1 Instruction: {:.9f} J\n".format(self.l1_instruction.idle_energy() + self.l1_instruction.active_energy()))
        
        print("Idle Consumption from L2: {:.9f} J".format((self.l2.idle_energy())))
        print("Active Consumption from L2: {:.9f} J".format((self.l2.active_energy())))
        print("Total Consumption from L2: {:.9f} J\n".format(self.l2.idle_energy() + self.l2.active_energy()))
        
        print("Idle Consumption from DRAM: {:.9f} J".format((self.dram.idle_energy())))
        print("Active Consumption from DRAM: {:.9f} J".format((self.dram.active_energy())))
        print("Total Consumption from DRAM: {:.9f} J\n".format(self.dram.idle_energy() + self.dram.active_energy()))
        
        print("Total Energy Consumption: {:.9f} J\n".format(self.total_energy()))
        
        print("Total Time: {:.10f} s".format(self.total_time()))
        print("Average Memory Access Time: {:.15f} s\n".format((self.total_time()) / self.total_accesses()))
        
        # print(Counter(self.l1_data.valid))
        # print(Counter(self.l1_instruction.valid))
        # print(Counter(self.l2.valid))
    
    def total_time(self):
        """
        Compute the total time processing all data.
        """
        return clock
    
    def total_energy(self):
        """
        Compute the total energy consumed by each memory structure.
        """
        return self.l1_data.idle_energy() + self.l1_data.active_energy() + \
            self.l1_instruction.idle_energy() + self.l1_instruction.active_energy() + \
            self.l2.idle_energy() + self.l2.active_energy() + \
            self.dram.idle_energy() + self.dram.active_energy()
    
    def total_accesses(self):
        """
        Compute the total number of accesses by each memory structure.
        """
        return self.l1_data.get_accesses() + self.l1_instruction.get_accesses() + \
            self.l2.get_accesses() + self.dram.get_accesses()

def main():
    # Assert that we have an input file
    if len(sys.argv) != 2:
        print("Usage: python CacheSim.py <input_file> or sim")
        sys.exit(1)
    
    filename = "./Traces/Spec_Benchmark/" + sys.argv[1]
    
    simulator = CacheSim(filename)
    simulator.run()
    simulator.report()

if __name__ == "__main__":
    main()