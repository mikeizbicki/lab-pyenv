'''
The refcount-gated in-place-resize fast path, in isolation.

CPython's += on str is only correct without a copy when the target
string is not aliased: if nobody else can observe the string, the
interpreter can extend its buffer in place; otherwise it must fall
back to allocate-and-copy, which turns an otherwise linear loop
into a quadratic one.

This file has two functions that produce the same output and differ
only in whether they hold a live alias inside the loop.  Time both
on the same pyenv version and compare.
'''
import sys


def concat_fast(n):
    '''
    No alias; the fast path is available on versions that have it.
    '''
    s = ''
    for _ in range(n):
        s += 'x'
    return s


def concat_slow(n):
    '''
    The same loop, plus one line that keeps the string aliased.
    '''
    s = ''
    other = s
    for _ in range(n):
        s += 'x'
        other = s
    return s


def show_refcounts(n=5):
    '''
    Print the refcount observed at the += site, once per iteration.
    The absolute value is version-dependent; the interesting detail
    is that it is > 1 whenever another name points at the string.
    '''
    s = ''
    for i in range(n):
        print(i, sys.getrefcount(s))
        s += 'x'
    return s


if __name__ == '__main__':
    show_refcounts()
