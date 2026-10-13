'''
Functions for measuring how CPython's runtimes (and in one case, its answers)
have changed between versions.

Every function below takes exactly one argument.
The `make_*` functions build the input data, and the other functions do the
work that we actually want to time.
Always build the data in timeit's setup code (the `-s` flag) so that you are
measuring the work and not the data generation.
'''

import math
import random
import sys


# Python 3.9.14, 3.10.7, and every version after them refuse to convert between
# very large ints and strings unless this limit is raised.  The limit exists to
# prevent denial-of-service attacks (converting a 10**9 digit string used to be
# an easy way to freeze a web server), and 0 means "no limit".
# Older patch releases of 3.9/3.10 do not have this function at all.
try:
    sys.set_int_max_str_digits(0)
except AttributeError:
    pass


ALPHABET = 'abcdefghijklmnopqrstuvwxyz'


################################################################################
# substring search
################################################################################

def make_adversarial(n):
    '''
    Build a (haystack, needle) pair that is maximally bad for the simple
    substring search algorithm.

    The haystack is n copies of 'a'.
    The needle is n//10 characters that are all 'a' except for the final 'b'.
    There is no match, but every single alignment of the needle against the
    haystack agrees for n//10 - 1 characters before failing on the last one.
    '''
    m = max(2, n // 10)
    haystack = 'a' * n
    needle = 'a' * (m - 1) + 'b'
    return haystack, needle


def make_random(n):
    '''
    Build a (haystack, needle) pair of exactly the same sizes as
    make_adversarial, but with random letters.

    There is (almost certainly) no match here either, but a mismatch is usually
    found on the very first character of the needle.
    '''
    m = max(2, n // 10)
    rng = random.Random(0)
    haystack = ''.join(rng.choice(ALPHABET) for _ in range(n))
    needle = ''.join(rng.choice(ALPHABET) for _ in range(m))
    return haystack, needle


def make_adversarial_bytes(n):
    '''
    The bytes version of make_adversarial.
    '''
    haystack, needle = make_adversarial(n)
    return haystack.encode(), needle.encode()


def find(pair):
    '''
    Search for the needle in the haystack, and report whether it was found.

    The `in` operator, str.find, str.index, str.count, str.replace, and
    str.split all use the same search routine inside CPython, so timing any one
    of them tells you about all of them.
    '''
    haystack, needle = pair
    return needle in haystack


################################################################################
# summing floats
################################################################################

def make_floats(n):
    rng = random.Random(0)
    return [rng.random() for _ in range(n)]


def sum_floats(xs):
    return sum(xs)


def sum_floats_loop(xs):
    '''
    The same thing, written out by hand.
    '''
    total = 0.0
    for x in xs:
        total += x
    return total


################################################################################
# converting between ints and strings
################################################################################

def make_digits(d):
    '''
    Build a string of d decimal digits.
    '''
    rng = random.Random(0)
    return rng.choice('123456789') + ''.join(
        rng.choice('0123456789') for _ in range(d - 1))


def make_bigint(d):
    '''
    Build an int with d decimal digits.
    '''
    return int(make_digits(d))


def str_to_int(s):
    return int(s)


def int_to_str(x):
    return str(x)


################################################################################
# values, not runtimes
################################################################################

def report_values():
    '''
    Print the exact value that each of these expressions evaluates to.

    Most of them are the same on every version of python.  The ones that are
    not are the entire point of this part of the lab.
    '''
    xs = [0.1] * 10
    ys = [1e100, 1.0, -1e100, 1.0]
    zs = [1e100, 1, -1e100, 1]
    cs = [complex(1e100, 1.0), complex(1.0, 1.0), complex(-1e100, 1.0)]
    big = make_bigint(10000)

    print('python                      =', sys.version.split()[0])
    print('sum([0.1]*10)               =', repr(sum(xs)))
    print('sum_floats_loop([0.1]*10)   =', repr(sum_floats_loop(xs)))
    print('math.fsum([0.1]*10)         =', repr(math.fsum(xs)))
    print('sum(ys)                     =', repr(sum(ys)))
    print('sum_floats_loop(ys)         =', repr(sum_floats_loop(ys)))
    print('math.fsum(ys)               =', repr(math.fsum(ys)))
    print('sum(zs)                     =', repr(sum(zs)))
    print('sum(cs)                     =', repr(sum(cs)))
    print('int(str(big)) == big        =', repr(int(str(big)) == big))
    print('len(str(big))               =', repr(len(str(big))))
    print("'b' in 'a'*1000             =", repr('b' in 'a' * 1000))
    print("('a'*999+'b') in 'a'*1000   =", repr(('a' * 999 + 'b') in 'a' * 1000))


if __name__ == '__main__':
    report_values()
