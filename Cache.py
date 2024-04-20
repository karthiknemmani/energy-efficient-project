import math
import random

class Cache:
    """
    Storage container for cache data. Used for L1 data, L1 instruction, and
    L2 caches.
    """
    def __init__(self, block_size, associativity, capacity, access_time, idle_consumption, active_consumption, transfer_penalty):
        # cache info
        self.block_size = block_size                    # in bytes
        self.associativity = associativity              # number of ways
        self.capacity = capacity                        # in bytes
        self.access_time = access_time                  # in seconds
        self.idle_consumption = idle_consumption        # in watts
        self.active_consumption = active_consumption    # in watts
        self.transfer_penalty = transfer_penalty        # in joules
        
        self.num_blocks = capacity // block_size
        sets = capacity // (block_size * associativity)
        
        self.block_bits = int(math.log2(block_size))
        self.cache_bits = int(math.log2(capacity))
        self.set_bits = int(math.log2(sets))
        self.set_offset = self.block_bits
        
        self.cache_mask = capacity - 1
        self.set_mask = sets - 1
        
        self.tag_offset = self.block_bits + self.set_bits
        
        # cache data
        self.tags = [0] * self.num_blocks
        self.valid = [False] * self.num_blocks
        self.dirty = [False] * self.num_blocks
        
        # stats
        self.accesses = 0
    
    def get_set(self, address):
        """
        Get the set number from the address.
        """
        address &= self.cache_mask
        return (address >> self.set_offset) & self.set_mask
    
    def get_tag(self, address):
        """
        Get the tag from the address.
        """
        address &= self.cache_mask
        return address >> self.tag_offset
    
    def access(self, access_type, address):
        if access_type == 2:
            # instruction fetch is essentially a read
            access_type = 0
        
        # index into set
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
                # set an invalid index for future writes
                invalid = i
                continue
            
            if tag != curr_tags[i]:
                continue
            
            hit = True
            
            curr_dirty[i] = access_type == 1
            break
        
        if not hit:
            index = -1
            if invalid != -1:
                curr_valid[invalid] = True
                index = invalid
            else:
                # evict a random cache block
                index = random.randint(0, self.associativity - 1)
                dirty = curr_dirty[index]
            
            curr_tags[index] = tag
            curr_dirty[index] = access_type == 1
        
        self.accesses += 1
        self.tags[block:block+self.associativity] = curr_tags
        self.valid[block:block+self.associativity] = curr_valid
        self.dirty[block:block+self.associativity] = curr_dirty
        
        return hit, dirty
                
        
        
        
        
        