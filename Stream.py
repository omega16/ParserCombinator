"""
Text Stream abstraction
"""

from io import StringIO

class Stream:
    def __init__(self, active_stream, state=None):
        self.stream = active_stream
        self.set_Stream_state(state)

    def set_Stream_state(self,state):
        pass
    
    @classmethod    
    def from_path(cls, rute):
        stream = open(rute,"r")
        out = cls(stream)
        out.pos = 0
        out.line = 1
        out.column = 1
        return out
        
    @classmethod
    def from_string(cls, string):
        stream = StringIO(string)
        out = cls(stream)    
        out.pos = 0
        out.line = 1
        out.column = 1
        return out

        
    def seek(self, state):
        """
        state must be the retrun of Stream.tell
        """
        self.stream.seek(state[0],0)
        self.pos, self.line, self.column = state[1:]

    def tell(self):
        return (self.stream.tell(), self.pos, self.line, self.column)

    def read(self,n=1):
        readed = self.stream.read(n)
        self.pos += len(readed)
        lines = readed.count("\n")
        if lines!=0:
            self.column = len(readed) - readed.rindex("\n")
            
        self.line+=lines
        return readed

    def lookup(self,n=1):
        state = self.tell()
        out = self.read(n)
        self.seek(state)
        return out




        
    
