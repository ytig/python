#!/usr/local/bin/python3
class uint:
    def __init__(self, generics):
        if isinstance(generics, int):
            self.value = generics & 0xFFFFFFFF
        elif isinstance(generics, (bytes, bytearray,)):
            self.value = int.from_bytes(generics, 'little') & 0xFFFFFFFF

    def __add__(self, other):
        assert isinstance(other, uint)
        return uint(self.value + other.value)

    def __sub__(self, other):
        assert isinstance(other, uint)
        return uint(self.value - other.value)

    def __mul__(self, other):
        assert isinstance(other, uint)
        return uint(self.value * other.value)

    def __div__(self, other):
        return self // other

    def __floordiv__(self, other):
        assert isinstance(other, uint)
        return uint(self.value // other.value)

    def __mod__(self, other):
        assert isinstance(other, uint)
        return uint(self.value % other.value)

    def __pow__(self, other):
        assert isinstance(other, uint)
        return uint(self.value**other.value)

    def __lshift__(self, other):
        assert isinstance(other, uint)
        return uint(self.value << other.value)

    def __rshift__(self, other):
        assert isinstance(other, uint)
        return uint(self.value >> other.value)

    def __and__(self, other):
        assert isinstance(other, uint)
        return uint(self.value & other.value)

    def __xor__(self, other):
        assert isinstance(other, uint)
        return uint(self.value ^ other.value)

    def __or__(self, other):
        assert isinstance(other, uint)
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

    def __eq__(self, other):
        assert isinstance(other, uint)
        return self.value == other.value

    def __ne__(self, other):
        assert isinstance(other, uint)
        return self.value != other.value

    def __gt__(self, other):
        assert isinstance(other, uint)
        return self.value > other.value

    def __lt__(self, other):
        assert isinstance(other, uint)
        return self.value < other.value

    def __ge__(self, other):
        assert isinstance(other, uint)
        return self.value >= other.value

    def __le__(self, other):
        assert isinstance(other, uint)
        return self.value <= other.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

    def __len__(self):
        return 4

    def __getitem__(self, index):
        return self.value.to_bytes(4, 'little')[index]
