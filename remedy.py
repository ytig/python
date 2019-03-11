#!/usr/local/bin/python3


# 取值
def safe_get(generics, k, d=None):
    if isinstance(generics, (tuple, list,)):
        l = len(generics)
        return generics[k] if k >= -l and k < l else d
    elif isinstance(generics, dict):
        return generics.get(k, d)
    raise TypeError


# 求和
def safe_sum(generics, *args):
    if isinstance(generics, tuple):
        return type(generics)(safe_sum(list(generics), *args))
    elif isinstance(generics, list):
        ret = generics.copy()
        for arg in args:
            ret.extend(arg)
        return ret
    elif isinstance(generics, dict):
        ret = generics.copy()
        for arg in args:
            ret.update(arg)
        return ret
    raise TypeError


# 过滤
def filter_items(generics, keep):
    if isinstance(generics, (tuple, list,)):
        return type(generics)(item[-1] for item in filter(keep, enumerate(generics)))
    elif isinstance(generics, dict):
        return type(generics)(filter(keep, generics.items()))
    raise TypeError


# 滤键
def key_in_list(generics, *keys):
    return filter_items(generics, lambda i: i[0] in keys)


# 滤值
def value_not_none(generics):
    return filter_items(generics, lambda i: i[-1] is not None)


# 可序列化
def isjson(obj):
    if obj is None:
        return True
    if obj in (False, True,):
        return True
    if isinstance(obj, int):
        return True
    if isinstance(obj, float):
        return obj == obj and obj != float('inf') and obj != float('-inf')
    if isinstance(obj, str):
        return True
    if isinstance(obj, (tuple, list,)):
        return all(isjson(i) for i in obj)
    if isinstance(obj, dict):
        return all(isinstance(k, str) for k in obj) and all(isjson(v) for v in obj.values())
    return False


# 负值（排序倒序）
class negative:
    def __init__(self, value):
        if not isinstance(value, negative):
            self.even = False
            self.value = value
        else:
            self.even = not value.even
            self.value = value.value

    def comparable(self, other):
        if not self.even:
            return isinstance(other, negative) and not other.even
        else:
            return not isinstance(other, negative) or other.even

    def __lt__(self, other):
        assert self.comparable(other)
        if not self.even:
            return self.value > other.value
        elif isinstance(other, negative):
            return self.value < other.value
        else:
            return self.value < other

    def __gt__(self, other):
        assert self.comparable(other)
        if not self.even:
            return self.value < other.value
        elif isinstance(other, negative):
            return self.value > other.value
        else:
            return self.value > other

    def __le__(self, other):
        assert self.comparable(other)
        if not self.even:
            return self.value >= other.value
        elif isinstance(other, negative):
            return self.value <= other.value
        else:
            return self.value <= other

    def __ge__(self, other):
        assert self.comparable(other)
        if not self.even:
            return self.value <= other.value
        elif isinstance(other, negative):
            return self.value >= other.value
        else:
            return self.value >= other

    def __eq__(self, other):
        assert self.comparable(other)
        if isinstance(other, negative):
            return self.value == other.value
        else:
            return self.value == other

    def __ne__(self, other):
        assert self.comparable(other)
        if isinstance(other, negative):
            return self.value != other.value
        else:
            return self.value != other
