from CacheBlock import CacheBlock

class CacheLine:
    def __init__(self, size, block_size, associativity):
        self.size = size
        self.block_size = block_size
        self.associativity = associativity
        self.blocks = [CacheBlock() for i in range(size // block_size)]
        
    def read(self, address):
        pass
        
    def write(self, address):
        pass