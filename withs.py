#!/usr/local/bin/python3
# coding:utf-8
import threading


class Stack:
    def __init__(self):
        self.stacks = {}

    # 线程标识
    @staticmethod
    def tid():
        return threading.currentThread().name

    # 入栈
    def push(self, data):
        k = Stack.tid()
        stack = self.stacks.get(k)
        if not stack:
            stack = []
            self.stacks[k] = stack
        stack.append(data)

    # 出栈
    def pop(self):
        k = Stack.tid()
        stack = self.stacks.get(k)
        if not stack or len(stack) <= 0:
            raise Exception('stack is empty.')
        return stack.pop(-1)


def _with2(Parent, Child):
    class family:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            self.__parent = Stack()
            self.__child = Stack()

        def __enter__(self):
            parent = Parent(*self.args, **self.kwargs)
            torch = parent.__enter__()
            try:
                child = Child(torch)
                torch = child.__enter__()
                self.__parent.push(parent)
                self.__child.push(child)
                return torch
            except BaseException as e:
                parent.__exit__(e.__class__, e, e.__traceback__)
                raise e

        def __exit__(self, type, value, traceback):
            child = self.__child.pop()
            parent = self.__parent.pop()
            try:
                child.__exit__(type, value, traceback)
            except BaseException as e:
                parent.__exit__(e.__class__, e, e.__traceback__)
                raise e
            parent.__exit__(type, value, traceback)
    return family


# 异常处理器嵌套
def withs(*args):
    l = len(args)
    if l <= 0:
        return None
    elif l == 1:
        return args[0]
    else:
        args = list(args)
        args[0] = _with2(args.pop(0), args[0])
        return withs(*args)
