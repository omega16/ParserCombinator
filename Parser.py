"""
Basic parser class for parser combinators
"""

from itertools import chain
from Stream import Stream


class ParserError(Exception):
    pass

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
            # state = stream.tell()
            # print("apply first ",self(stream))
            # stream.seek(state)
            return [*chain.from_iterable(
                function(data)(stream) for data, stream_state in self(stream)
                )]
        return Parser(binded)


    def __rshift__(self, other):
        return self.bind(other)

    @classmethod
    def unit(cls, data):
        return cls(lambda stream: [(data, stream.tell())])

    @classmethod
    def zero(cls):
        return cls(lambda stream: [])

    @classmethod
    def item(cls):
        def out(stream):
            if actual := stream.read(1):
                return [(actual, stream.tell())]
            return []
        return cls(out)

    def __or__(self, other):
        def out(stream):
            if parsed1 := self(stream):
                return [parsed1[0]]
            if parsed2 := other(stream):
                return [parsed2[0]]
            return []
        return Parser(out)

    def __add__(self, other):
        def out(stream):
            state = stream.tell()
            if parsed1 := self(stream):
                if parsed2 := other(stream):
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
                return [(actual, stream.tell())]
        stream.seek(state)
        return []
    return Parser(out)

def char(char_value):
    return sat(lambda x: char_value ==x)


def all_of(*parsers):
    p = parsers[0]
    for p1 in parsers[1:]:
        p = p+p1
    return p

def first_of(*parsers):
    p = parsers[0]
    for p1 in parsers[1:]:
        p = p|p1
    return p
 

def many(p):
    return p>>(lambda x1: many(p)>>(lambda x2: Parser.unit([x1, *x2])))|Parser.unit([])


def many1(p):
    return p>>(
        lambda x1: many(p)>>(
            lambda x2: Parser.unit([x1, *x2])
        )
    )

def sepby1(p,sep):
    return p>>(
        lambda x1 : many(
            sep>>(
                lambda x2: p>> (
                    lambda x3: Parser.unit(x3)
                ) 
            ) 
        )>> (lambda x4: Parser.unit([x1, *x4]) )
    )

def sepby(p,sep):
    return sepby1(p, sep)|Parser.unit([])


def parser_raise(msg):
    def aux(stream, *args):
        raise ParserError("At {}\n{}\n".format(repr(stream), msg))
    return Parser(aux)

def error_bracket(open_bracket, p, close_bracket, closed_char=None):
    if closed_char:
        error_msg = "Unbalanced bracket, expected '{}' ".format(closed_char)
    else :
        error_msg = "Some bracket is unbalanced "
    return open_bracket >> (
            lambda x1: p >>(
                lambda x2: (
                    (close_bracket|parser_raise(error_msg))>>(
                        lambda x3: Parser.unit(x2)
                    )
                )
            )
        )

def bracket(open_bracket, p, close_bracket):
    return open_bracket >> (
        lambda x1: p >>(
            lambda x2: (
                close_bracket>>(
                    lambda x3: Parser.unit(x2)
                )
            )
        )
    )


def from_iterable(ite):
    def aux(current):
        return lambda x : x==current
    acc = []
    for i in ite:
        acc.append(sat(aux(i)))
    return acc

def token(name):
    return lambda x: Parser.unit((name,x))


letter = sat(lambda x: "a" <= x <= "z")
letters = many1(letter)>>(lambda x: Parser.unit("".join(x)))
List = sepby(letters, char(","))

special = first_of(*from_iterable("~@"))


def main():
    letter = sat(lambda x: "a" <= x <= "z")
    letters = many1(letter)>>(lambda x: Parser.unit("".join(x)))
    List = sepby(letters, char(","))

    special = first_of(*from_iterable("~@"))
    
    # p1 = sat(lambda x: "a"<=x<="z")
    # p = many1(p1)>>(lambda x: Parser.unit("".join(x)))
    # p=error_bracket(char("["), List, char("]"))
    p = error_bracket(char("["), List, char("]"),"]")>>token("list")
    # p = special
    stream = Stream.from_string(input())
    print(p(stream))

    
if __name__ == "__main__":
    main()
