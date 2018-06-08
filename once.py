#!/usr/local/bin/python3
# coding:utf-8


# 单次调用（装饰器）
def once(crash=False):
    def decorator(function):
        rets = []

        def wrapper(*args, **kwargs):
            if not getattr(function, 'called', False):
                setattr(function, 'called', True)
                rets.append(function(*args, **kwargs))
            elif crash:
                raise Exception('this method can only be used once.')
            return rets[-1] if len(rets) > 0 else None
        return wrapper
    return decorator
