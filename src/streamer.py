import random

class streamer:

    def __init__(self):
        self.header_pos = random.randint(10, 50)*1000
        self.count = 0
    
    def getNext(self):
        self.count += 1
        if self.count == self.header_pos:
            return 'x'
        elif self.count == self.header_pos + 1:
            return 'A'
        elif self.count == self.header_pos + 2:
            return 'd'
        else:
            return chr(random.randint(0,255))
        
        