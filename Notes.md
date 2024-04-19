## Initial notes:  

### Dinero arguments:  
    - Access type  
    - Memory address  
    - Data being written or read  

### Access types:  
    0: Memory read.  
    1: Memory write.  
    2: Instruction fetch.  
    3: Ignore.  
    4: Flush the cache.  
    
### Implementing L1 and L2 cache including directory/data:  
    - Cache is divided into directory structure  
    - Tags for cache lines are stored  
    - Data part consists of cache lines storing the data  
    
### Speed:  
    - Assume reading next line in trace takes .5 nanoseconds, unless processor stalled  
        - Processor speed is 2 GHz  
        - If there are previous reads that didn't finish, processor must wait  
    
### Implementation:  
    - Writeback policy  
    - L2 cache has set associativity of 4  
        - Then, experiment with set associativity of 2, 4, and 8  
    - L1 always directly mapped  
    - Cache replacement algorithm is random  
    
### Basic Assumptions:  
    - Assume all cache misses can be found in DRAM  
    - Entire cache line must be present when writing to cache or brought from  
    the next level in the hierarchy  
        - Thus, write miss will invoke a read operation before writing  
    - Transfers between L1 and L2, and between L2 and DRAM are done in units  
    of 64 bytes  

### Questions:
    - Can we assume that we read/write into DRAM at 64 bytes at a time?