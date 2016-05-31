import random
from enum import IntEnum

class StreamError(Exception): # Create an user-defined exceptio to test stream errors
    def __init__(self, value):
         self.value = value
    def __str__(self):
        return repr(self.value)

class Status(IntEnum): 
    SUCCESS = 0
    TIMEOUT = 1
    FAILURE = 2
    
    
class Streamer:
    def __init__(self):
        self.header_pos = random.randint(10, 50)*1000 # The "xAd" header is found at this position
        self.count = 0
        
        # The logic below makes sure that the stream times out 10% of the time, fails 20% of the time, otherwise succceeds.
        chance = random.randint(0,99)
        if chance % 5==0:
            self.outcome = Status.FAILURE
        elif chance % 7==0:
            self.outcome = Status.TIMEOUT
        else:
            self.outcome = Status.SUCCESS
    
    def getNext(self):
        self.count += 1
        
        # When count reaches header position a successful stream will return header "xAd" is 3 successive calls to get_next()
        if self.outcome == Status.SUCCESS:  
            if self.count == self.header_pos:
                return 'x'
            elif self.count == self.header_pos + 1:
                return 'A'
            elif self.count == self.header_pos + 2:
                return 'd'
                
        # A failure stream will raise an exception when the header position is reached.
        if self.outcome == Status.FAILURE and self.count == self.header_pos:
            raise StreamError("")
        
        # We try to avoid inserting  "xAd" by random chance by converting all "x" to "b"
        ch = chr(random.randint(0,255))
        if ch == "x":
            ch = "b"
        return ch
        
        