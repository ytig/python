#!/usr/local/bin/python3
import collections
import inquirer


# 选择
def choose(message, choices, default=None):
    if isinstance(choices, (tuple, list,)):
        assert choices
        return inquirer.prompt([inquirer.List('', message=message, choices=choices, default=default)], raise_keyboard_interrupt=True)['']
    elif isinstance(choices, collections.OrderedDict):
        return choices[choose(message, list(choices), default=default)]
    raise TypeError
