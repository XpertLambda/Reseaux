class AObj:
    def __init__(self, a):
        self.a = a
    def __repr__(self):
        return f"A<{self.a}> "

class BObj:
    def __init__(self,aobj, b):
        self.aobj = aobj
        self.b = b
    def __repr__(self):
        return  f"B<{self.b}> " + self.aobj.__repr__()

class PyObj:
    def __init__(self, aobj, bobj, c):
        self.aobj = aobj
        self.bobj = bobj
        self.c = c
    def __repr__(self):
        return self.aobj.__repr__() + self.bobj.__repr__() + f"C<{self.c}> "
