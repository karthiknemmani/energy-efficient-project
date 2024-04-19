class CacheBlock:
    def __init__(self, tag, valid, dirty, data):
        self.tag = tag
        self.valid = valid
        self.dirty = dirty
        self.data = data
        
    def write(self, tag):
        self.tag = tag
        self.valid = True
        self.dirty = True
    
    def read(self):
        pass
        