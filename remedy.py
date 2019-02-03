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
