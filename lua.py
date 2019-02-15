#!/usr/local/bin/python3


# 语言兼容
def lua_compat(generics):
    if isinstance(generics, tuple):
        l = list(generics)
        return lua_compat(l)
    elif isinstance(generics, list):
        d = dict(enumerate([None, ] + generics))
        d.pop(0)
        return lua_compat(d)
    elif isinstance(generics, dict) and not isinstance(generics, table):
        for k in generics:
            generics[k] = lua_compat(generics[k])
        return table(generics)
    else:
        return generics


class table(dict):
    def copy(self):
        return type(self)(self)

    def lists(self):
        return [self[i + 1] for i in range(len(self))]

    def append_(self, object):
        self[len(self) + 1] = object

    def clear_(self):
        return self.clear()

    def copy_(self):
        return self.copy()

    def count_(self, value):
        c = 0
        for v in self.values():
            if v == value:
                c += 1
        return c

    def extend_(self, iterable):
        if isinstance(iterable, table):
            for i in range(len(iterable)):
                self[len(self) + 1] = iterable[i + 1]
        else:
            for i in iterable:
                self[len(self) + 1] = i

    def index_(self, value, start=None, stop=None):
        if start is None:
            start = 0
        elif start < 0:
            start += len(self)
        if stop is None:
            stop = len(self)
        elif stop < 0:
            stop += len(self)
        for i in range(max(start, 0), min(stop, len(self))):
            if self[i + 1] == value:
                return i
        raise ValueError('%s is not in table' % repr(value))

    def insert_(self, index, object):
        if index < 0:
            index += len(self)
            index = max(index, 0)
        else:
            index = min(index, len(self))
        for i in range(len(self) - 1, -1, -1):
            if i >= index:
                self[i + 2] = self[i + 1]
                if i == index:
                    self[i + 1] = object
                    break
            else:
                self[len(self) + 1] = object
                break

    def pop_(self, index=-1):
        if index < 0:
            index += len(self)
        r = []
        for i in range(len(self)):
            if not r:
                if i == index:
                    r.append(self[i + 1])
            else:
                self[i] = self[i + 1]
        if not r:
            raise IndexError('pop index out of range')
        del self[len(self)]
        return r.pop()

    def remove_(self, value):
        r = []
        for i in range(len(self)):
            if not r:
                if self[i + 1] == value:
                    r.append(i)
            else:
                self[i] = self[i + 1]
        if not r:
            raise ValueError('table.remove_(x): x not in table')
        del self[len(self)]

    def reverse_(self):
        for i, v, in enumerate(reversed([self[i + 1] for i in range(len(self))])):
            self[i + 1] = v

    def sort_(self, key=None, reverse=False):
        for i, v, in enumerate(sorted([self[i + 1] for i in range(len(self))], key=key, reverse=reverse)):
            self[i + 1] = v
