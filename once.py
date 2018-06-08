#!/usr/local/bin/python3
# coding:utf-8


# 单次调用（装饰器）
def once(crash=False):
    def decorator(function):
        def wrapper(self, *args, **kwargs):
            ret = None
            if not getattr(self, function.__qualname__, False):
                setattr(self, function.__qualname__, True)
                ret = function(self, *args, **kwargs)
            elif crash:
                raise Exception('this method can only be used once.')
            return ret
        return wrapper
    return decorator
