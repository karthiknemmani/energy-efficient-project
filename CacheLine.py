# don't use yet
class CacheLine:
    def __init__(self, associativity):
        self.tags = [0] * associativity
        self.valid = False
        self.dirty = False
        self.occupied = 0
    
    def set_valid(self, valid):
        self.valid = valid
    
    def set_dirty(self, dirty):
        self.dirty = dirty
        
    def set_tag(self, tag):
        if self.occupied < len(self.tags):
            self.tags[self.occupied] = tag
            self.occupied += 1
        else:
            # implement eviction
            pass
        
    