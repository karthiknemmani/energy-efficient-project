import math
import random


class MemorySystem:
    def __init__(self, access_time, idle_consumption, active_consumption, transfer_penalty, lower_access_time=0, lower_transfer_penalty=0):
        self.access_time = access_time
        self.idle_consumption = idle_consumption
        self.active_consumption = active_consumption
        self.transfer_penalty = transfer_penalty
        self.lower_transfer_penalty = lower_transfer_penalty
        self.accesses = 0
        self.writebacks = 0
        self.lower_access_time = lower_access_time

    def access(self):
        raise NotImplementedError
    
    def writeback(self):
        raise NotImplementedError
    
    def active_energy(self):
        return (self.active_consumption * self.access_time + self.transfer_penalty) * self.accesses + \
            (self.active_consumption * (self.access_time - self.lower_access_time) + \
            (self.transfer_penalty - self.lower_transfer_penalty)) * self.writebacks

    def total_time(self):
        return self.access_time * self.accesses + self.writebacks * (self.access_time - self.lower_access_time)
    
    def idle_watts(self):
        return self.idle_consumption
    
    def active_watts(self):
        return self.active_consumption
    
    def get_accesses(self):
        return self.accesses
    
    def get_writebacks(self):
        return self.writebacks
    
    
class Cache(MemorySystem):
    def __init__(self, block_size, associativity, capacity, access_time, idle_consumption, active_consumption, transfer_penalty, lower_access_time, lower_transfer_penalty):
        super().__init__(access_time, idle_consumption, active_consumption, transfer_penalty, lower_access_time, lower_transfer_penalty)
        self.block_size = block_size
        self.associativity = associativity
        self.capacity = capacity
        
        self.num_blocks = capacity // block_size
        sets = capacity // (block_size * associativity)
        
        self.block_bits = int(math.log2(block_size))
        self.cache_bits = int(math.log2(capacity))
        self.set_bits = int(math.log2(sets))
        self.cache_mask = capacity - 1
        self.set_mask = sets - 1
        self.tag_offset = self.block_bits + self.set_bits
        
        self.tags = [-1] * self.num_blocks
        self.valid = [False] * self.num_blocks
        self.dirty = [False] * self.num_blocks
        self.misses = 0
        
        self.access_dict = {set: 0 for set in range(sets)}
    
    def get_set(self, address):
        return (address >> self.block_bits) & self.set_mask
    
    def get_tag(self, address):
        tag_size = 32 - (self.block_bits + self.set_bits)
        return (address >> self.tag_offset) & ((1 << tag_size) - 1)
    
    def access(self, access_type, address):
        set_index = self.get_set(address)
        tag = self.get_tag(address)
        
        block = set_index * self.associativity
        curr_tags, curr_valid, curr_dirty = \
            self.tags[block:block+self.associativity], \
            self.valid[block:block+self.associativity], \
            self.dirty[block:block+self.associativity]
        
        dirty = False
        hit = False
        invalid = -1
        for i in range(len(curr_valid)):
            if not curr_valid[i]:
                invalid = i
                continue
            
            if tag == curr_tags[i]:
                hit = True
                curr_dirty[i] |= access_type == 1
                break
        
        evicted_address = 0
        index = -1
        if not hit:
            self.misses += 1
            
            if invalid != -1:
                index = invalid
            else:
                index = random.randint(0, self.associativity - 1)
                dirty = curr_dirty[index]
                
                if dirty:
                    # reconstruct address
                    evicted_address = self.construct_address(curr_tags[index], set_index)
                    
            curr_tags[index] = tag
            curr_valid[index] = True
            curr_dirty[index] = access_type == 1
            
        self.accesses += 1
        
        self.access_dict[set_index] += 1
        self.tags[block:block+self.associativity] = curr_tags
        self.valid[block:block+self.associativity] = curr_valid
        self.dirty[block:block+self.associativity] = curr_dirty
        
        return hit, dirty, evicted_address, index
    
    def construct_address(self, tag, set_index):
        return (tag << self.tag_offset) | (set_index << self.block_bits)
    
    def writeback(self, address):
        """
        Writeback, lower level of cache to this level. Only used by L2.
        """
        set_index = self.get_set(address)
        tag = self.get_tag(address)
        
        block = set_index * self.associativity
        curr_tags, curr_valid, curr_dirty = \
            self.tags[block:block+self.associativity], \
            self.valid[block:block+self.associativity], \
            self.dirty[block:block+self.associativity]
        for i in range(len(curr_valid)):
            if curr_valid[i] and tag == curr_tags[i]:
                curr_dirty[i] = True
                self.writebacks += 1
                self.dirty[block:block+self.associativity] = curr_dirty
                break
        

    
    def cache_fill(self, address, index):
        set_index = self.get_set(address)
        tag = self.get_tag(address)
        
        block = set_index * self.associativity
        
        self.tags[block+index] = tag
        self.valid[block+index] = True
        self.dirty[block+index] = False
    
    def get_misses(self):
        return self.misses
    
    def get_hits(self):
        return self.accesses - self.misses

class DRAM(MemorySystem):
    def __init__(self):
        super().__init__(5e-8, 0.8, 4, 6.4e-10, 5e-9, 5e-12)
    
    def access(self):
        """
        Increment data accesses, also used when writing back to DRAM.
        """
        self.accesses += 1
    
    def writeback(self):
        """
        Writeback to DRAM.
        """
        self.writebacks += 1