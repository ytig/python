#!/usr/local/bin/python3
import collections


class _int:
    # 类型转换
    @classmethod
    def format(cls, generics):
        if type(generics) is cls:
            return generics
        else:
            return cls(generics)

    # 运算优先级
    @classmethod
    def priority(cls):
        return -1

    def __init__(self, value):
        self.value = value

    def __neg__(self):
        return type(self)(-self.value)

    def __pos__(self):
        return type(self)(+self.value)

    def __invert__(self):
        return type(self)(~self.value)

    def __add__(self, other):
        tp1 = type(self)
        tp2 = type(other)
        if isinstance(other, _int) and tp2.priority() > tp1.priority():
            return other.__radd__(self)
        else:
            return tp1(self.value + tp1.format(other).value)

    def __sub__(self, other):
        tp1 = type(self)
        tp2 = type(other)
        if isinstance(other, _int) and tp2.priority() > tp1.priority():
            return other.__rsub__(self)
        else:
            return tp1(self.value - tp1.format(other).value)

    def __mul__(self, other):
        tp1 = type(self)
        tp2 = type(other)
        if isinstance(other, _int) and tp2.priority() > tp1.priority():
            return other.__rmul__(self)
        else:
            return tp1(self.value * tp1.format(other).value)

    def __div__(self, other):
        return self // other

    def __floordiv__(self, other):
        tp1 = type(self)
        tp2 = type(other)
        if isinstance(other, _int) and tp2.priority() > tp1.priority():
            return other.__rfloordiv__(self)
        else:
            return tp1(self.value // tp1.format(other).value)

    def __mod__(self, other):
        tp1 = type(self)
        tp2 = type(other)
        if isinstance(other, _int) and tp2.priority() > tp1.priority():
            return other.__rmod__(self)
        else:
            return tp1(self.value % tp1.format(other).value)

    def __pow__(self, other):
        tp1 = type(self)
        tp2 = type(other)
        if isinstance(other, _int) and tp2.priority() > tp1.priority():
            return other.__rpow__(self)
        else:
            return tp1(self.value ** tp1.format(other).value)

    def __lshift__(self, other):
        tp1 = type(self)
        tp2 = type(other)
        if isinstance(other, _int) and tp2.priority() > tp1.priority():
            return other.__rlshift__(self)
        else:
            return tp1(self.value << tp1.format(other).value)

    def __rshift__(self, other):
        tp1 = type(self)
        tp2 = type(other)
        if isinstance(other, _int) and tp2.priority() > tp1.priority():
            return other.__rrshift__(self)
        else:
            return tp1(self.value >> tp1.format(other).value)

    def __and__(self, other):
        tp1 = type(self)
        tp2 = type(other)
        if isinstance(other, _int) and tp2.priority() > tp1.priority():
            return other.__rand__(self)
        else:
            return tp1(self.value & tp1.format(other).value)

    def __xor__(self, other):
        tp1 = type(self)
        tp2 = type(other)
        if isinstance(other, _int) and tp2.priority() > tp1.priority():
            return other.__rxor__(self)
        else:
            return tp1(self.value ^ tp1.format(other).value)

    def __or__(self, other):
        tp1 = type(self)
        tp2 = type(other)
        if isinstance(other, _int) and tp2.priority() > tp1.priority():
            return other.__ror__(self)
        else:
            return tp1(self.value | tp1.format(other).value)

    def __iadd__(self, other):
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
        return self ** other

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
        return type(self)(other) + self

    def __rsub__(self, other):
        return type(self)(other) - self

    def __rmul__(self, other):
        return type(self)(other) * self

    def __rdiv__(self, other):
        return type(self)(other) / self

    def __rfloordiv__(self, other):
        return type(self)(other) // self

    def __rmod__(self, other):
        return type(self)(other) % self

    def __rpow__(self, other):
        return type(self)(other) ** self

    def __rlshift__(self, other):
        return type(self)(other) << self

    def __rrshift__(self, other):
        return type(self)(other) >> self

    def __rand__(self, other):
        return type(self)(other) & self

    def __rxor__(self, other):
        return type(self)(other) ^ self

    def __ror__(self, other):
        return type(self)(other) | self

    def __eq__(self, other):
        tp1 = type(self)
        tp2 = type(other)
        if isinstance(other, _int) and tp2.priority() > tp1.priority():
            return tp2.format(self).value == other.value
        else:
            return self.value == tp1.format(other).value

    def __ne__(self, other):
        tp1 = type(self)
        tp2 = type(other)
        if isinstance(other, _int) and tp2.priority() > tp1.priority():
            return tp2.format(self).value != other.value
        else:
            return self.value != tp1.format(other).value

    def __gt__(self, other):
        tp1 = type(self)
        tp2 = type(other)
        if isinstance(other, _int) and tp2.priority() > tp1.priority():
            return tp2.format(self).value > other.value
        else:
            return self.value > tp1.format(other).value

    def __lt__(self, other):
        tp1 = type(self)
        tp2 = type(other)
        if isinstance(other, _int) and tp2.priority() > tp1.priority():
            return tp2.format(self).value < other.value
        else:
            return self.value < tp1.format(other).value

    def __ge__(self, other):
        tp1 = type(self)
        tp2 = type(other)
        if isinstance(other, _int) and tp2.priority() > tp1.priority():
            return tp2.format(self).value >= other.value
        else:
            return self.value >= tp1.format(other).value

    def __le__(self, other):
        tp1 = type(self)
        tp2 = type(other)
        if isinstance(other, _int) and tp2.priority() > tp1.priority():
            return tp2.format(self).value <= other.value
        else:
            return self.value <= tp1.format(other).value

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, index):
        return self.value.to_bytes(len(self), 'little')[index]

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)


class uint8(_int):
    @classmethod
    def priority(cls):
        return 0

    def __init__(self, generics):
        if isinstance(generics, _int):
            value = generics.value
        elif isinstance(generics, int):
            value = generics
        elif isinstance(generics, bytes):
            value = int.from_bytes(generics, 'little')
        elif isinstance(generics, str):
            value = int.from_bytes(bytes(generics, 'ascii'), 'little')
        elif isinstance(generics, collections.Iterable):
            value = int.from_bytes(bytes(generics), 'little')
        else:
            raise TypeError
        super().__init__(value & 0xFF)

    def __len__(self):
        return 1


class uint(_int):
    @classmethod
    def priority(cls):
        return 1

    def __init__(self, generics):
        if isinstance(generics, _int):
            value = generics.value
        elif isinstance(generics, int):
            value = generics
        elif isinstance(generics, bytes):
            value = int.from_bytes(generics, 'little')
        elif isinstance(generics, str):
            value = int.from_bytes(bytes(generics, 'ascii'), 'little')
        elif isinstance(generics, collections.Iterable):
            value = int.from_bytes(bytes(generics), 'little')
        else:
            raise TypeError
        super().__init__(value & 0xFFFFFFFF)

    def __len__(self):
        return 4
