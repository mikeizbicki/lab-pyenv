'''
Building up a string (or a bytes, or a bytearray) one piece at a time.

Read all of the functions in this file before running any of them.
The only difference between the `fast` and `slow` versions is a single line
that appears to do nothing at all.
'''

import sys


def make_seed():
    '''
    Build a one-character string.

    This looks like a silly way to write 'x', and it is, but it matters.
    A string literal like 'x' is *interned*: there is exactly one such object,
    it is shared by every part of your program that mentions it, and in recent
    versions of python it is also *immortal* (python has stopped counting
    references to it at all).  Building the string at runtime instead gives us
    an ordinary string object that nobody else has a reference to.
    '''
    return ''.join(['x'])


################################################################################
# strings
################################################################################

def concat_fast(n):
    '''
    Append to a string n times.
    '''
    s = make_seed()
    for i in range(n):
        s += 'x'
    return len(s)


def concat_slow(n):
    '''
    Append to a string n times, with one extra line that stores a second
    reference to the string before each append.

    The variable `alias` is never read.  Deleting the line would not change the
    value that this function returns.
    '''
    s = make_seed()
    for i in range(n):
        alias = s
        s += 'x'
    return len(s)


def concat_join(n):
    '''
    Collect the pieces in a list and join them at the end.
    '''
    parts = []
    for i in range(n):
        parts.append('x')
    return len(''.join(parts))


################################################################################
# bytes and bytearray
################################################################################

def concat_bytes_fast(n):
    '''
    The same loop as concat_fast, on a bytes object instead of a str.
    '''
    b = bytes(b'x')
    for i in range(n):
        b += b'x'
    return len(b)


def concat_bytes_slow(n):
    '''
    The same loop as concat_slow, on a bytes object instead of a str.
    '''
    b = bytes(b'x')
    for i in range(n):
        alias = b
        b += b'x'
    return len(b)


def concat_bytearray(n):
    '''
    The same loop, on a bytearray.

    A bytearray is *mutable*, and it deliberately allocates more room than it
    currently needs (the same trick that makes list.append fast).  It therefore
    does not need to care about how many references point at it.
    '''
    b = bytearray(b'x')
    for i in range(n):
        b += b'x'
    return len(b)


################################################################################
# reporting
################################################################################

def show_refcounts(n):
    '''
    Print how many references point at the string at the moment that each `+=`
    is about to run.

    sys.getrefcount itself needs a reference to the object you hand it, so its
    answer is always one larger than the number of references in your program.
    The subtraction below undoes that.  Do not read anything into the exact
    numbers; the only question worth asking is whether the count is 1 or more
    than 1.
    '''
    print('concat_fast:')
    s = make_seed()
    for i in range(n):
        print('  i={} refcount={}'.format(i, sys.getrefcount(s) - 1))
        s += 'x'

    print('concat_slow:')
    s = make_seed()
    for i in range(n):
        alias = s
        print('  i={} refcount={}'.format(i, sys.getrefcount(s) - 1))
        s += 'x'

    print('concat_bytes_fast:')
    b = bytes(b'x')
    for i in range(n):
        print('  i={} refcount={}'.format(i, sys.getrefcount(b) - 1))
        b += b'x'


def report_build():
    '''
    Print which python this is and whether it has a GIL.
    '''
    print('version    =', sys.version.split()[0])
    try:
        print('gil        =', sys._is_gil_enabled())
    except AttributeError:
        print('gil        = True (this build has no free-threading option)')


if __name__ == '__main__':
    report_build()
    show_refcounts(5)
