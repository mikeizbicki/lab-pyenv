'''
Algorithms for the pyenv runtime lab.

Every function in this file is small enough to be timed with
`python3 -m timeit` on a single line.  The functions that take a
size parameter n are meant to be called with n chosen so that the
runtime lands in the 1e-6 to 1e-1 second range on a modern CPU.

Doctests are deliberately omitted: the interesting behavior of
these functions is in the runtime and (for a few of them) in the
exact value they return, and neither of those is expressible in a
doctest.
'''
import math
import sys


# The 3.11 release capped int<->str conversion at 4300 digits so
# that the quadratic algorithm could not be used as a DoS vector;
# 3.12 then replaced the algorithm with a subquadratic one.  Lift
# the cap so the timings are visible.  (3.9 and 3.10 do not have
# the cap, and so do not have the setter.)
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)


# ---------------------------------------------------------------------------
# Baseline pure-Python loops
# ---------------------------------------------------------------------------

def loop_sum(n):
    '''A trivial python-level loop.'''
    s = 0
    for i in range(n):
        s += i
    return s


def fib_rec(n):
    '''
    Naive recursive Fibonacci.  Exponential; use n <= 30 with timeit.
    '''
    if n < 2:
        return n
    return fib_rec(n - 1) + fib_rec(n - 2)


def try_pass(n):
    '''
    A loop whose body is wrapped in a try/except with no exception
    raised on the happy path.  Pre-3.11, every iteration paid a
    SETUP_FINALLY; post-3.11, the cost is close to zero.
    '''
    s = 0
    for i in range(n):
        try:
            s += i
        except ValueError:
            pass
    return s


# ---------------------------------------------------------------------------
# += on str and bytes
# ---------------------------------------------------------------------------

def concat_plus(n):
    '''Build an n-character string by repeated +=.'''
    s = ''
    for _ in range(n):
        s += 'x'
    return s


def concat_bytes(n):
    '''Same as concat_plus, but for bytes.'''
    b = b''
    for _ in range(n):
        b += b'x'
    return b


def concat_alias(n):
    '''
    Same as concat_plus, but hold a live alias to s inside the
    body.  The alias forces the refcount at the += site above 1,
    which defeats the in-place-resize fast path on every version.
    Negative control for Part 2.
    '''
    s = ''
    keep = None
    for _ in range(n):
        keep = s
        s += 'x'
    return s


def concat_join(n):
    '''
    Build an n-character string with ''.join.  Expected to be
    Theta(n) on every version, with no cliff.  Negative control.
    '''
    return ''.join(['x'] * n)


# ---------------------------------------------------------------------------
# bigint <-> str
# ---------------------------------------------------------------------------

def int_to_str_big(N):
    '''str(2**N); N is the bit length of the input integer.'''
    return str(2 ** N)


def str_to_int_big(N):
    '''int('9' * N); N is the number of decimal digits.'''
    return int('9' * N)


# ---------------------------------------------------------------------------
# gcd and modular inverse
# ---------------------------------------------------------------------------

def gcd_inputs(N):
    '''
    Return a tuple of two N-bit integers whose gcd is nontrivial.
    Deterministic so that every version is timed on the same pair
    (and so that students get the same numbers as each other).
    '''
    d = (1 << (N // 2)) - 1
    a = ((1 << N) - 1) * d
    b = ((1 << (N - 1)) - 1) * d
    return (a, b)


def gcd_stress(pair):
    '''math.gcd on a pair built by gcd_inputs.'''
    a, b = pair
    return math.gcd(a, b)


def modinv_inputs(N):
    '''
    Return (e, phi) with gcd(e, phi) == 1 and both N bits, suitable
    for modinv_stress.
    '''
    e = (1 << (N - 1)) | 1
    phi = 1 << N
    return (e, phi)


def modinv_stress(pair):
    '''
    pow(e, -1, phi), python 3.8+.  Extended Euclid, i.e. gcd.  This
    is the operation RSA key generation uses to compute the private
    exponent d from the public exponent e and Euler's totient phi,
    and it is therefore on the critical path of every https request.
    '''
    e, phi = pair
    return pow(e, -1, phi)


# ---------------------------------------------------------------------------
# sum of floats
# ---------------------------------------------------------------------------

def sum_float(n):
    '''
    sum([0.1] * n).  Same Theta(n) on every version, but the value
    changes at the 3.12 boundary, which switched sum() of floats to
    Neumaier compensated summation.
    '''
    return sum([0.1] * n)


def sum_float_cancellation():
    '''
    The canonical demonstration of compensated summation: 0.0 on
    <=3.11, 1.0 on >=3.12.
    '''
    return sum([1e16, 1.0, -1e16])


# ---------------------------------------------------------------------------
# string formatting
# ---------------------------------------------------------------------------

def fstr(n):
    '''f-string in a loop.'''
    x = 42
    for _ in range(n):
        s = f'{x}'
    return s


def format_(n):
    '''str.format in a loop.'''
    x = 42
    for _ in range(n):
        s = '{}'.format(x)
    return s


def pct(n):
    '''%-formatting in a loop.'''
    x = 42
    for _ in range(n):
        s = '%s' % x
    return s


# ---------------------------------------------------------------------------
# value report
# ---------------------------------------------------------------------------

def report_values():
    '''
    Print the value that each Part 1 function returns on this
    version of python.  Students run this once per version to fill
    in the second (value) table in the README.
    '''
    print('python      =', sys.version.split()[0])
    print('concat_plus =', repr(concat_plus(5)))
    print('concat_bytes=', repr(concat_bytes(5)))
    print('concat_join =', repr(concat_join(5)))
    print('int_to_str  =', repr(int_to_str_big(64)))
    print('str_to_int  =', repr(str_to_int_big(20)))
    print('sum_float   =', repr(sum_float(10)))
    print('sum_cancel  =', repr(sum_float_cancellation()))
    print('fstr        =', repr(fstr(1)))
    print('format_     =', repr(format_(1)))
    print('pct         =', repr(pct(1)))
    e, phi = modinv_inputs(16)
    print('modinv      =', modinv_stress((e, phi)))
