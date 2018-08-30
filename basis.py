#!/usr/local/bin/python3
import collections


class uint:
    @staticmethod
    def make(generics):
        if isinstance(generics, uint):
            return generics
        else:
            return uint(generics)

    def __init__(self, generics):
        if isinstance(generics, int):
            self.value = generics & 0xFFFFFFFF
        elif isinstance(generics, bytes):
            self.value = int.from_bytes(generics, 'little') & 0xFFFFFFFF
        elif isinstance(generics, str):
            self.value = int.from_bytes(bytes(generics, 'ascii'), 'little') & 0xFFFFFFFF
        elif isinstance(generics, collections.Iterable):
            self.value = int.from_bytes(bytes(generics), 'little') & 0xFFFFFFFF
        else:
            raise TypeError

    def __add__(self, other):
        other = uint.make(other)
        return uint(self.value + other.value)

    def __sub__(self, other):
        other = uint.make(other)
        return uint(self.value - other.value)

    def __mul__(self, other):
        other = uint.make(other)
        return uint(self.value * other.value)

    def __div__(self, other):
        return self // other

    def __floordiv__(self, other):
        other = uint.make(other)
        return uint(self.value // other.value)

    def __mod__(self, other):
        other = uint.make(other)
        return uint(self.value % other.value)

    def __pow__(self, other):
        other = uint.make(other)
        return uint(self.value**other.value)

    def __lshift__(self, other):
        other = uint.make(other)
        return uint(self.value << other.value)

    def __rshift__(self, other):
        other = uint.make(other)
        return uint(self.value >> other.value)

    def __and__(self, other):
        other = uint.make(other)
        return uint(self.value & other.value)

    def __xor__(self, other):
        other = uint.make(other)
        return uint(self.value ^ other.value)

    def __or__(self, other):
        other = uint.make(other)
        return uint(self.value | other.value)

    def __iaddr__(self, other):
        return self + other

    def __isub__(self, other):
        return self - other

    def __imul__(self, other):
        return self * other

    def __idiv__(self, other):
        return self / other

    def __ifloordiv__(self, other):
        return self // other

    def __imod__(self, other):
        return self % other

    def __ipow__(self, other):
        return self**other

    def __ilshift__(self, other):
        return self << other

    def __irshift__(self, other):
        return self >> other

    def __iand__(self, other):
        return self & other

    def __ixor__(self, other):
        return self ^ other

    def __ior__(self, other):
        return self | other

    def __radd__(self, other):
        return uint(other) + self

    def __rsub__(self, other):
        return uint(other) - self

    def __rmul__(self, other):
        return uint(other) * self

    def __rdiv__(self, other):
        return uint(other) / self

    def __rfloordiv__(self, other):
        return uint(other) // self

    def __rmod__(self, other):
        return uint(other) % self

    def __rpow__(self, other):
        return uint(other)**self

    def __rlshift__(self, other):
        return uint(other) << self

    def __rrshift__(self, other):
        return uint(other) >> self

    def __rand__(self, other):
        return uint(other) & self

    def __rxor__(self, other):
        return uint(other) ^ self

    def __ror__(self, other):
        return uint(other) | self

    def __eq__(self, other):
        other = uint.make(other)
        return self.value == other.value

    def __ne__(self, other):
        other = uint.make(other)
        return self.value != other.value

    def __gt__(self, other):
        other = uint.make(other)
        return self.value > other.value

    def __lt__(self, other):
        other = uint.make(other)
        return self.value < other.value

    def __ge__(self, other):
        other = uint.make(other)
        return self.value >= other.value

    def __le__(self, other):
        other = uint.make(other)
        return self.value <= other.value

    def __len__(self):
        return 4

    def __getitem__(self, index):
        return self.value.to_bytes(4, 'little')[index]

    def __neg__(self):
        return uint(-self.value)

    def __pos__(self):
        return uint(+self.value)

    def __invert__(self):
        return uint(~self.value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)
