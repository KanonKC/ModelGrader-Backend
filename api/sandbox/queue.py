class Queue():
    def __init__(self,SIZE) -> None:
        self.memory = [0 for i in range(SIZE)]
        self.size = SIZE
    
    def isAvaliable(self) -> int:
        for i in range(self.size):
            if self.memory[i] == 0:
                return i
        return -1
    
    def reserve(self,index:int) -> None:
        self.memory[index] = 1
    
    def free(self,index:int) -> None:
        self.memory[index] = 0