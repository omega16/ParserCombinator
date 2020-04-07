"""
Basic parser class for parser combinators
"""

from itertools import chain
from Stream import Stream


class Parser:
    def __init__(self, function):
        """
        function(Stream) -> [(Data, Stream_state)]
        is spected that Data implements the ">>" operator
        >>(Data(some), f) -> f(some)
        and "f" uses "some" to instantiate Data in some way.
        """
        self.function = function

    def __call__(self, stream):
        return self.function(stream)

    def bind(self, function):
        """
        function(Data(some1)) -> Parser( f(Stream) -> [(Data(some2), Stream_state)] )
        """
        def binded(stream):
            #state = stream.tell()
            #print("apply first ",self(stream))
            #stream.seek(state)
            return [*chain.from_iterable( function(data)(stream) for data, stream_state in self(stream) )]
        return Parser(binded)

    @classmethod
    def unit(cls, data):
        return cls(lambda stream : [(data,stream.tell())])

    @classmethod
    def zero(cls):
        return cls(lambda stream : [])
        
    @classmethod
    def item(cls):
        def out(stream):
            if (actual := stream.read(1)):
                return [(actual,stream.tell())]
            else:
                return []
        return cls(out)

    def __or__(self,other):
        def out(stream):
            if parsed1 := self(stream):
                return [parsed1[0]]
            parsed2 = other(stream)
            return [parsed2[0]]
        return Parser(out)

    def __add__(self,other):
        def out(stream):
            state = stream.tell()
            if parsed1 := self(stream):
                if parsed2 := other(stream):
                    print("p1 ",parsed1)
                    print("p2 ",parsed2)
                    return parsed1+parsed2
                stream.seek(state)
                return []
            return []
        return Parser(out)
                
        

def sat(bool_f):
    def out(stream):
        state = stream.tell()
        if (actual := stream.read(1)):
            if bool_f(actual):
                return [(actual,stream.tell())]
        stream.seek(state)
        return []
    return Parser(out)

def char(char_value):
    return sat(lambda x : char_value==x)
    
non_zero_digit = sat(lambda x : "1"<=x<="9")
digit = sat(lambda x: "0"<=x<="9")

def all_of(*parsers):
    p = parsers[0]
    for p1 in parsers[1:]:
        p = p+p1
    return p

def first_of(*parsers):
    def out(stream):
        for p in parsers:
            if out:= p(stream):
                return out
        return []
    return out
    
def many(p):
    return p.bind(lambda x1 : p.bind(lambda x2 : Parser.unit(x1+x2))) + Parser.unit([[]])   


def many1(p):
    def out(stream):
        if parsed := p(stream):
            return parsed+many(p)(stream)
        return []
    return out
        

def join(p):
    def out(stream):
        if parsed := p(stream):
            chain.from_iterable()

def main():
    p1 = sat(lambda x: "a"<=x<="z")
    p = p1.bind(lambda x1 : (p1+Parser.unit([])).bind(lambda x2: Parser.unit(x1+x2) ) ) 
    #p =p1+(p1|Parser.unit("jaja"))
    stream = Stream.from_string(input())
    print(p(stream))

    
if __name__ == "__main__":
    main()

        


            
            


            

    
