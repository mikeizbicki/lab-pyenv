'''
Catastrophic backtracking, and why the master theorem does not
apply.

CPython's re module uses a backtracking engine.  The pattern
(a+)+$ on the input 'a'*n + 'b' has no match, but every way of
splitting the run of a's between the two nested quantifiers is
tried before the engine gives up, which is about 2**n attempts.

The point of this file for the lab is that the fix is a different
LIBRARY, not a different python version.  A Thompson-NFA or DFA
engine -- re2, Go's regexp, Rust's regex -- matches the same
pattern against the same string in time Theta(n * m), where m is
the size of the pattern.  But swapping CPython's re engine out
for a Thompson NFA would change the set of strings matched by some
other patterns, and would therefore break the contract that
re.match has with its users.  CPython can lower gcd's exponent
freely because gcd is fully specified by its input/output
relation; it cannot switch regex engines without breaking
compatibility.
'''
import re
import time


PATTERN = r'(a+)+$'


def matches(n):
    '''
    Run the backtracking pattern on 'a'*n + 'b'.  Returns None (the
    pattern does not match); the return value is only kept so that
    CPython cannot optimize the call away.
    '''
    return re.match(PATTERN, 'a' * n + 'b')


def sweep(ns=(16, 18, 20, 22, 24)):
    '''
    Print n and wall-clock seconds for a range of n.  Each doubling
    of n should square the runtime if the engine is backtracking,
    and roughly double it if the engine is a Thompson NFA.
    '''
    print('pattern:', PATTERN)
    for n in ns:
        t0 = time.perf_counter()
        matches(n)
        dt = time.perf_counter() - t0
        print('n={:3d}  {:.6e} s'.format(n, dt))


if __name__ == '__main__':
    sweep()
