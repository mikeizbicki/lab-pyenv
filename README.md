# Lab: pyenv and runtimes across Python versions

<!--
INSTRUCTOR NOTES -- NOT STUDENT-FACING

Pedagogical point of the lab: CPython's stdlib contract is O(.),
not Theta(.).  That leaves the implementers free to change the
constant (often), the exponent (rare), and, in at least one place,
the exact return value that a stdlib function produces.  The lab
forces students to MEASURE those changes rather than read about
them, and then to explain them with the master theorem where that
is possible.

Things students should discover, not be told:

  * str += in a loop is Theta(n^2) on some versions and Theta(n)
    on others.  I am not certain of the exact minor version where
    the in-place-resize fast path was lost and restored; it is in
    the 3.11/3.12 window (the BINARY_OP rewrite and the
    specialization it gained back).  Do not leak a version number;
    the point is that students sweep.
  * sum() of a list of floats returns a different value on 3.12+
    than on 3.11-.  This is the capital column of the lab: it is
    the only row where the O(.) contract fails to protect the
    caller from a change in output.

Things we decided NOT to ask students for, and why:

  * We do not run bigO on int<->str or gcd.  Those rows have
    Delta-k < 0.5, which is not separable from noise by any
    reasonable AIC fit on a 2-3 decade sweep.  Only concat_plus
    and concat_bytes have Delta-k >= 0.7 and are handed to bigO.
  * We do not ask students to fit a class to fib_rec; its
    recurrence is not aT(n/b) + f(n), and we use that fact to
    motivate the master theorem's preconditions.
  * We do not ask students to install re2 or change regex engines.
    The regex section is a conceptual contrast, not a measurement.

Additional context for revising this assignment later:

  * The regex / ReDoS section is deliberately a contrast, not an
    instance of the master theorem.  Its purpose is to make the
    point that "fix by version bump" and "fix by different library"
    are different operations with different compatibility
    consequences.
  * The RSA / inverses section is written, not measured.  It sits
    next to the gcd row because gcd is the engine of RSA key
    generation, and because factoring is the problem that RSA
    depends on being hard.  Pointers to MATH55 (discrete math)
    and CSCI148 (graph algorithms) are in the text.
  * img/ is not included in this commit; add one called
    img/meme.jpg.
  * The homework this lab precedes is a numeric programming
    library (polynomials with exact coefficients, forward-mode
    autodiff in the style of pytorch).  The lab's
    aliasing/refcount story and its sum_float result-change story
    both reappear in the homework, as the reasons for requiring a
    hand-written __iadd__ and for using Fraction coefficients
    rather than float.
-->

<img src=img/meme.jpg width=300px />

CPython publishes only $O(\cdot)$ bounds on its standard library.
That is not an oversight: it leaves the implementers free to change
the constant factor, the exponent, or, in rare cases, the exact
value a function returns, without breaking any documented promise.
In this lab you will install several versions of python and *measure*
what actually changed between them.

**Learning objectives**

1. install and switch between python minors with `pyenv`
2. measure runtime with `timeit`
3. see that CPython guarantees only $O(\cdot)$, never $\Theta(\cdot)$
4. apply the master theorem to the standard library itself
5. distinguish "fix by upgrading python" from "fix by choosing a
   different library"

## Part 0: pyenv

Fork this repo and clone it on the lambda server.

Install the python minors:
```
$ pyenv install 3.9 3.10 3.11 3.12 3.13
$ pyenv versions
```

`pyenv local` writes a `.python-version` file that selects the python
for the current directory.  This repo ships one pinned to 3.13;
switch it with
```
$ pyenv local 3.11
$ python3 --version
```

Verify that each version works before moving on.

> **NOTE:** 3.9 and 3.10 are end-of-life as of this writing.  We keep
> them here because the interesting changes land in the 3.11 and 3.12
> windows, and having both sides of the boundary is the whole point.

## Part 1: the big table

`algorithms.py` contains one function per row below.  Each takes a
single size parameter `n` (bit length for `int_to_str_big`, digit
length for `str_to_int_big`, iteration count for everything else).
The general form of the timing command is
```
$ python3 -m timeit -s 'import algorithms; n = 4096' 'algorithms.concat_plus(n)'
```

For the two functions that take a precomputed pair, build the pair in
the setup code:
```
$ python3 -m timeit -s 'import algorithms; p = algorithms.gcd_inputs(4096)' 'algorithms.gcd_stress(p)'
```

Choose `n` per row so that the runtime lands between roughly 1e-6 and
1e-1 seconds on the fastest version.  Fill the table with **seconds**,
in the format that `timeit` prints.

|                     | 3.9 | 3.10 | 3.11 | 3.12 | 3.13 |
| ------------------- | --- | ---- | ---- | ---- | ---- |
| `loop_sum`          |     |      |      |      |      |
| `fib_rec`           |     |      |      |      |      |
| `try_pass`          |     |      |      |      |      |
| `concat_plus`       |     |      |      |      |      |
| `concat_bytes`      |     |      |      |      |      |
| `concat_alias`      |     |      |      |      |      |
| `concat_join`       |     |      |      |      |      |
| `int_to_str_big`    |     |      |      |      |      |
| `str_to_int_big`    |     |      |      |      |      |
| `gcd_stress`        |     |      |      |      |      |
| `modinv_stress`     |     |      |      |      |      |
| `sum_float`         |     |      |      |      |      |
| `fstr`              |     |      |      |      |      |
| `format_`           |     |      |      |      |      |
| `pct`               |     |      |      |      |      |

> **HINT:** you can automate the sweep with a `for` loop and `seq`,
> exactly like in `lab-timeit2`.  See that lab's README for details.

### 1b: the value table

A few of these functions return a *different value* on different
versions.  The runtime table cannot show that, so fill a second table
with the exact values:
```
$ python3 -c 'import algorithms; algorithms.report_values()'
```

|                            | 3.9 | 3.10 | 3.11 | 3.12 | 3.13 |
| -------------------------- | --- | ---- | ---- | ---- | ---- |
| `concat_plus(5)`           |     |      |      |      |      |
| `concat_bytes(5)`          |     |      |      |      |      |
| `concat_join(5)`           |     |      |      |      |      |
| `int_to_str_big(64)`       |     |      |      |      |      |
| `str_to_int_big(20)`       |     |      |      |      |      |
| `sum_float(10)`            |     |      |      |      |      |
| `sum_float_cancellation()` |     |      |      |      |      |
| `fstr(1)`                  |     |      |      |      |      |
| `format_(1)`               |     |      |      |      |      |
| `pct(1)`                   |     |      |      |      |      |

Every cell in this table should equal every other cell in its row,
except where the semantics of the underlying function changed between
versions.  For each row that does change, write one sentence saying
what changed.

## Part 2: refcounts and the `+=` fast path

`concat.py` isolates the mechanism behind the `concat_plus` row of
Part 1.

CPython can implement `s += 'x'` without a copy whenever the string
is not aliased: if the reference count at the `+=` site is 1, then
nobody else can observe the buffer, so it can be resized in place.
If the string *is* aliased, `+=` must fall back to allocate-and-copy,
and a loop of `n` such operations costs $\Theta(n^2)$ instead of
$\Theta(n)$.

Read the three functions in `concat.py`, then:

1. Run `concat_fast` and `concat_slow` under `timeit` on each version,
   with `n` large enough that the slower of the two is visibly slower.

2. Run `show_refcounts(5)`.  The absolute numbers differ between
   versions; the interesting thing is which iteration shows a
   refcount greater than 1.

Write a paragraph answering: is the fast path present on all
versions, only some, or does it depend on the caller's code?  Your
answer should agree with the `concat_plus` row of the Part 1 table.

> **NOTE:** this is the "innocuous change" punchline of the lab: one
> extra line of code that *looks like it does nothing* -- aliasing a
> variable -- changes the asymptotics of the whole loop.

## Part 3: fit the asymptotics with bigO

`timeit` gives a single number per cell.  To *identify* the
asymptotic class, install the `bigO` package:
```
$ pip3 install -r requirements.txt
```
and apply `@bigO.track` to a function whose size parameter you
declare with a length function:
```python
import bigO

@bigO.track(lambda n: n)
def concat_plus_tracked(n):
    s = ''
    for _ in range(n):
        s += 'x'
    return s
```

Drive the function over a geometric sweep, for example
`for n in range(100, 100_000, 100): concat_plus_tracked(n)`, run the
script under each `pyenv local`, and then
```
$ python3 -m bigO
```
which produces `bigO.pdf` with the fitted curve for each tracked
function.

**Only two rows of the Part 1 table should be handed to `bigO`:**
`concat_plus` and `concat_bytes`.  Every other row is either
$O(1)$-per-call, a pure constant-factor change, or has an exponent
change that is too small for the AIC fitter to separate from noise on
a 2-3 decade sweep.  Fitting those rows will produce a graph that
looks meaningful but is not.

Fit `concat_plus` and `concat_bytes` on each version, and record the
fitted exponent $k$ in the table below:

|                | 3.9 | 3.10 | 3.11 | 3.12 | 3.13 |
| -------------- | --- | ---- | ---- | ---- | ---- |
| `concat_plus`  |     |      |      |      |      |
| `concat_bytes` |     |      |      |      |      |

> **NOTE:** `bigO` reports one of `O(1)`, `O(log log n)`, `O(log n)`,
> `O(log(n)**2)`, `O(log(n)**3)`, `O(sqrt(n))`, `O(n)`, `O(n*log(n))`,
> `O(n**2)`, `O(n**3)`, `O(n**k)`, `O(2**n)`.  Report the *exponent*
> when it is reported as `O(n**k)`: `k=1.98` vs `k=1.01` is a much
> more honest signal than `O(n**2)` vs `O(n)`.

## Part 4: master theorem

Every column of the Part 1 table is $O(\cdot)$-bounded, but not every
function has a recurrence of the form
$$T(n) = a\,T(n/b) + f(n)$$
that the master theorem handles.  In this part you will sort them.

### 4a: recurrences

For each of the following, write down the recurrence, decide whether
the master theorem applies, and if it does, solve it.

- `concat_join` (iterative)
- `concat_alias` (the $\Theta(n^2)$ loop)
- `concat_plus` **on a version where the fast path is present**
- `fib_rec`
- `gcd_stress`
- `int_to_str_big` / `str_to_int_big`

For the gcd and int-to-str rows, express the recurrence in terms of
the *bit length* $b$ and the cost $M(b)$ of a big-integer multiply of
two $b$-bit numbers.  Both algorithms have the same recurrence,
$$T(b) = 2T(b/2) + \Theta(M(b)).$$
Solve it twice: once with the schoolbook $M(b) = \Theta(b^2)$ and once
with Karatsuba $M(b) = \Theta(b^{\log_2 3})$.  Comparing the two
solutions is what makes it possible for the *same* gcd algorithm to
get faster across a few versions without changing its specification.

For `fib_rec`, write the recurrence and explain why the master
theorem does not apply.  Use it to state the precondition of the
master theorem.

### 4b: catastrophic backtracking (`regex.py`)

`regex.py` times a single pattern against a single family of strings.
Read the file, run `regex.sweep()`, and record the results.

The pattern `(a+)+$` matched against `'a'*n + 'b'` has no match, but
has roughly $2^n$ ways to fail: every split of the run of `a`'s
between the outer and inner quantifier is tried before the engine
gives up.  Doubling `n` squares the runtime.

> **NOTE:** patterns of this kind are the basis for a class of
> denial-of-service attacks called **ReDoS**.  Cloudflare (2019) and
> Stack Overflow (2016) are famous incidents.  The exploit is
> entirely in the difference between polynomial and exponential
> runtime.

The fix is not a version upgrade.  A different *class* of regex
engine -- the Thompson NFA, used by `re2` (google), `regexp` (Go),
and `regex` (Rust) -- matches the same pattern against the same
string in $\Theta(nm)$ time, where $m$ is the pattern length.

Why can't CPython just switch?  Because `re.match` is specified by a
*pattern language* and the *matching semantics*, not by a runtime
bound.  A Thompson-NFA engine would accept a different set of strings
for some patterns and would break every program that relies on the
backtracking engine's behavior.  Contrast with `gcd_stress`: the
output of `gcd(a, b)` is specified completely by its input-output
relation, so the *implementation* is free to change, and the exponent
can move across a version boundary without any compatibility cost.

> **ASIDE:** this is the same fact that lets CPython lower the
> exponent of `int(str)` between versions.  A "function" in the
> mathematical sense owes you an output; it does not owe you an
> algorithm.

### 4c: what does $O(\cdot)$ protect you from?

Look at the `sum_float` row in both Part 1 tables.  The *runtime* row
shows $\Theta(n)$ on every version (the constant goes *up* a hair at
the 3.12 boundary).  The *value* row changes at that boundary, in the
direction of a more accurate result: CPython switched `sum` of floats
to Neumaier compensated summation.

This is the only row where a version upgrade *worsens* the constant
factor in order to improve the result.  It is a reminder of what the
$O(\cdot)$ contract does and does not do:

- it says nothing about the constant factor,
- it says nothing about the *value* of the function, and
- it is the reason numerical code (including the homework for this
  lab) prefers exact coefficients -- `int`, `Fraction` -- over
  `float`.

### 4d: inverses, and why https

Some functions are easy to invert and some are not.  This is not a
property of "functions" as a category, and two easy-looking examples
sit right next to each other in this lab:

- `int_to_str_big` and `str_to_int_big` are inverses, and both are
  fast.
- `gcd_stress` and `modinv_stress` are also inverses (`modinv` undoes
  a modular multiplication via extended Euclid), and both are fast.

Now consider modular exponentiation, which every https connection
performs thousands of times per second:

- Forward: `pow(b, e, m)`.  Square-and-multiply, $\Theta(\log e)$
  multiplications.  Every TLS handshake runs this.
- Inverse: given $b^e \bmod m$ and $(b, e, m)$, recover $b$.  This is
  the *discrete logarithm* problem.  No polynomial-time algorithm is
  known.
- Key generation: `d = pow(e, -1, phi)` -- that is the extended-Euclid
  calculation in `modinv_stress`.  **The `modinv_stress` row of the
  Part 1 table is on the critical path of every https request your
  browser makes.**

The teachable line:

> https is secure because gcd is fast and factoring is (believed to
> be) slow.  CPython can lower gcd's exponent freely; the security of
> the internet depends on the direction it cannot touch.

Every other function in the Part 1 table is easy to invert *and* easy
to evaluate.  Both facts matter, and either one alone would be
misleading.

For more: MATH55 (discrete math) covers the number theory; CSCI148
(graph algorithms) covers the network side and the asymptotic bounds
used informally in this lab.

## Submission

Commit to your fork:

- both tables from Part 1, filled in for all five versions
- the `bigO.pdf` and `bigO_data.json` files from Part 3, plus the
  exponent table
- written answers to Parts 2 and 4, in a `NOTES.md` file

Submit the url to canvas.
