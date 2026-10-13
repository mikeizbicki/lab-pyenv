'''
This file exists only to check which version of python you are running.

The `match` statement was added in python 3.10.
It is a *syntax* feature, which means that older versions of python cannot
even read this file; they fail before running a single line of it.

Run this file under each of your installed pythons.
'''

import sys


def describe(x):
    match x:
        case 0:
            return 'zero'
        case [_, _]:
            return 'a pair'
        case str():
            return 'a string'
        case _:
            return 'something else'


if __name__ == '__main__':
    print('this python is', sys.version)
    for x in [0, [1, 2], 'pi', 3.14]:
        print(' ', repr(x), '->', describe(x))
