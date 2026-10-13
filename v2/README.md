# Lab: pyenv, and what changes between versions of python

In this lab you will install two versions of python side by side and measure
what actually changed between them.

<img src=img/meme.jpg width=300px />

Python's documentation tells you what a function *returns*.
It almost never tells you how long the function will take,
and it never promises that the answer will be bit-for-bit the same next year.
That is not an oversight.
A function in the mathematical sense owes you an output;
it does not owe you an algorithm.
That freedom is what lets CPython's authors replace a quadratic algorithm in
the standard library with a linear one, in a patch you did not read,
in a release you upgraded to by accident.

In this lab you will watch three such replacements happen,
and one case where the *answer itself* changed.

**Learning objectives**

1. use `pyenv` to install and switch between versions of python
1. measure a change in asymptotic runtime instead of reading about it
1. apply the master theorem to the standard library itself

## Part 0: pyenv

Fork this repo, clone it on the lambda server, and `cd` into the `v2` folder.

The `pyenv` program installs as many versions of python as you like into your
home directory, without touching the system python.
Install the three that this lab needs:
```
$ pyenv install 3.9
$ pyenv install 3.14
$ pyenv install 3.14t
```
and check that they are all there:
```
$ pyenv versions
```

The last one is python 3.14 built in *free-threaded* mode.
We will not use it until Part 2.

> **NOTE:**
> Python 3.14 is the "pi-thon" release.
> This is the only time in your career that the version number of your
> programming language will be a mathematical constant,
> so enjoy it.
> (Python 3.141 is scheduled for the year 2155.)

`pyenv local` writes a file called `.python-version` into the current
directory, and from then on `python3` in that directory means that version.
This folder ships with a `.python-version` pinned to 3.9.
Switch it like this:
```
$ pyenv local 3.14
$ python3 -VV
```

The `-VV` flag prints the full version, including the patch number and the
date the binary was built.
**Write down the exact output of `python3 -VV` for each of your three
installs.**
You will put these at the top of your tables.
Patch numbers matter in this lab: some of the behavior you are about to
measure was changed in a patch release and then backported to older versions.

Now verify that each install really works.
The file `matchcheck.py` uses the `match` statement, which was added to the
language in python 3.10:
```
$ pyenv local 3.14
$ python3 matchcheck.py
$ pyenv local 3.9
$ python3 matchcheck.py
```

You should see the second command fail with a `SyntaxError`.

> **NOTE:**
> Look carefully at *where* it fails.
> It does not print the version line and then crash;
> it never runs any code at all.
> `match` is a change to python's grammar, so python 3.9 cannot even finish
> reading the file.
> This is a different kind of incompatibility than the ones you will measure
> in the rest of the lab, and it is the only kind that is impossible to
> overlook.

> **NOTE:**
> Python 3.9 reached "end of life" in October 2025, which means it receives no
> more fixes of any kind, including security fixes.
> Do not ship anything on it.
> We install it here because it is the most recent version that predates all
> of the changes we want to look at.

## Part 1: the table

The file `algorithms.py` contains the functions you will time.
Read it before continuing.

Every function takes exactly one argument.
The functions whose names start with `make_` build the input data, and the
rest do the work.
We always build the data in `timeit`'s setup code (the `-s` flag) so that we
are measuring the work and not the data generation:
```
$ python3 -m timeit \
    -s 'import algorithms; pair = algorithms.make_adversarial(2**13)' \
    'algorithms.find(pair)'
```

### 1a: runtimes

Fill in the table below with measured runtimes.
Report the number that `timeit` prints, including its units.

|                                   | 3.9 | 3.14 |
| --------------------------------- | --- | ---- |
| `find(make_adversarial(2**13))`   |     |      |
| `find(make_adversarial(2**14))`   |     |      |
| `find(make_adversarial(2**15))`   |     |      |
| `find(make_adversarial(2**16))`   |     |      |
| `find(make_random(2**13))`        |     |      |
| `find(make_random(2**14))`        |     |      |
| `find(make_random(2**15))`        |     |      |
| `find(make_random(2**16))`        |     |      |
| `sum_floats(make_floats(2**20))`  |     |      |
| `str_to_int(make_digits(10**4))`  |     |      |
| `str_to_int(make_digits(10**5))`  |     |      |
| `int_to_str(make_bigint(10**4))`  |     |      |
| `int_to_str(make_bigint(10**5))`  |     |      |

> **HINT:**
> You do not have to run these one at a time.
> Use a shell `for` loop over `seq`, exactly like in `lab-timeit2`:
> ```
> $ for i in $(seq 13 16); do
>     echo "i=$i"
>     python3 -m timeit \
>         -s "import algorithms; pair = algorithms.make_adversarial(2**$i)" \
>         'algorithms.find(pair)'
> done
> ```

> **NOTE:**
> Some of the cells in the 3.9 column will take a long time.
> If a cell is going to take more than about a minute, you can force `timeit`
> to do less work with `-n 1 -r 3`, which runs the code once per repeat and
> repeats three times.
> If a cell is *still* too slow, write `>60s` in the table and move on.

Now answer these in `NOTES.md`:

1. For `make_adversarial`, how does the runtime change when you double `n`,
   on each version?  Write down the multiplier you observe.
   What exponent `k` does that multiplier correspond to, in the sense that
   runtime grows like $n^k$?

1. For `make_random`, how does the runtime change when you double `n`,
   on each version?

1. The adversarial and random inputs have exactly the same sizes.
   They are the same number of characters, and the needle is absent from the
   haystack in both cases.
   Why is one of them so much worse than the other on 3.9?
   (Read the docstring of `make_adversarial` again.)

1. On one version, `find` takes about the same amount of time on both inputs.
   For a function that has this property, is there any input a hostile user
   could send you that would make it slow?

> **NOTE:**
> Here is what changed, which you are not expected to have guessed.
> Through python 3.9, `str.find` and friends used a simple scanning algorithm
> with a skip table.  It is very fast on ordinary text and quadratic on
> repetitive text.
> Python 3.10 added the Crochemore-Perrin "two-way" algorithm, which is
> $\Theta(n + m)$ in the *worst* case, where $n$ is the length of the haystack
> and $m$ is the length of the needle.
> You will not be asked to learn how it works.
>
> There is a catch that will bite you if you pick your own values of `n`:
> the two-way algorithm has a setup cost, so CPython only bothers to use it
> once the strings are big enough.  The exact cutoff is an implementation
> detail that has been re-tuned more than once.  For needles shorter than
> roughly a hundred characters, both versions do the same thing, and the table
> shows nothing.

### 1b: values

The runtime table cannot show you a change in the *answer*.
This command prints the answers:
```
$ python3 algorithms.py
```

Run it under each version and fill in the table.
Copy the values exactly as printed, including every digit.

|                                 | 3.9 | 3.14 |
| ------------------------------- | --- | ---- |
| `sum([0.1]*10)`                 |     |      |
| `sum_floats_loop([0.1]*10)`     |     |      |
| `math.fsum([0.1]*10)`           |     |      |
| `sum(ys)`                       |     |      |
| `sum_floats_loop(ys)`           |     |      |
| `math.fsum(ys)`                 |     |      |
| `sum(zs)`                       |     |      |
| `sum(cs)`                       |     |      |
| `int(str(big)) == big`          |     |      |
| `'b' in 'a'*1000`               |     |      |
| `('a'*999+'b') in 'a'*1000`     |     |      |

Most of these rows are the same in both columns, and that is the normal case:
the algorithm underneath `in` changed completely between these two versions
and the answer did not move at all.

For each row that *is* different, write one sentence in `NOTES.md` saying what
changed.

> **NOTE:**
> Here is what changed.
> Adding floating point numbers is not associative: `(a + b) + c` and
> `a + (b + c)` can give different answers, because each addition rounds.
> Adding a list of floats left to right accumulates that rounding error.
> Python 3.12 changed the built-in `sum` to use *Neumaier summation*, which
> keeps a running correction term for the bits that each addition threw away,
> and python 3.13 extended it to complex numbers.
> `math.fsum` has always done something even more careful (and even slower).
>
> Notice that the `zs` row contains ints mixed in with the floats, and does
> not change.  `sum` only takes its compensated path when every element is
> exactly a float; one int in the list and you are back to naive addition.
> A change in the answer that depends on the *types* in your list is a
> genuinely unpleasant thing to debug.

Finally, time the sum again on both versions and compare it against the
timing you already recorded:
```
$ python3 -m timeit \
    -s 'import algorithms; xs = algorithms.make_floats(2**20)' \
    'algorithms.sum_floats_loop(xs)'
```

In `NOTES.md`: is `sum` still $\Theta(n)$ on both versions?
Did the constant factor go up or down?
Did the hand-written loop's answer change?

## Part 2: aliasing, reference counts, and the GIL

This part is different from the rest of the lab.
Everywhere else, the thing that changes is the version of python.
Here, the thing that changes is **one line in your own code**, and the effect
is the same on both versions.

Read all of `concat.py` before running anything.

The two interesting functions are `concat_fast` and `concat_slow`.
They differ by one line:
```python
        alias = s
```
The variable `alias` is never read.
Deleting the line cannot change what the function returns.

Time them both, on both versions:
```
$ python3 -m timeit -s 'import concat' 'concat.concat_fast(2**14)'
$ python3 -m timeit -s 'import concat' 'concat.concat_slow(2**14)'
```
Then do it again at `2**15` and `2**16`.

|                     | `n=2**14` | `n=2**15` | `n=2**16` |
| ------------------- | --------- | --------- | --------- |
| `concat_fast`       |           |           |           |
| `concat_slow`       |           |           |           |
| `concat_join`       |           |           |           |
| `concat_bytes_fast` |           |           |           |
| `concat_bytes_slow` |           |           |           |
| `concat_bytearray`  |           |           |           |

(Fill this table in for 3.14.  You do not need to repeat it for 3.9, but spot
check one row to confirm that the story is the same there.)

Here is the mechanism.
Strings in python are *immutable*, so `s += 'x'` is supposed to build a brand
new string and copy the old contents into it, which makes a loop of `n` of
them $\Theta(n^2)$.
But CPython cheats.
Every object carries a count of how many references point at it.
If that count is 1 at the moment `+=` runs, then the string you are about to
throw away is one that *nobody else can see*, so CPython is allowed to resize
it in place and skip the copy.
The loop becomes $\Theta(n)$.

Storing a second reference destroys the trick, because now somebody else can
see the buffer.
You can watch the counts yourself:
```
$ python3 concat.py
```

In `NOTES.md`, write a paragraph answering:
which loop shows a reference count greater than 1, on which iterations, and
how does that line up with the runtimes you measured?

> **NOTE:**
> Three warnings about this trick, because it is less solid than it looks.
>
> First, it is a *permission*, not a promise.  Strings do not reserve spare
> room the way lists do, so resizing in place only works if the memory
> allocator happens to have free space immediately after the string.  When it
> does not, you pay for a copy anyway.
>
> Second, it depends on where your variable lives.  In python 3.11 the
> optimization was narrowed so that it only fires for ordinary local variables
> inside a function.  The identical loop written at the top level of a script,
> or on a global, or on a variable captured by a closure, lost it.  You cannot
> see this with `python3 -m timeit`, because `timeit` wraps your statement in
> a function before running it, which quietly puts you back in the fast case.
>
> Third, `sys.getrefcount` needs a reference to its own argument, so it always
> reports one more than the number of references in your program.  Never trust
> the absolute number; only ask whether it is 1 or more than 1.

### 2a: bytes

Now look at your `concat_bytes_fast` and `concat_bytes_slow` rows.
The code is identical to the string versions except for the `b` prefixes.

You should find that `alias` makes no difference at all, because `bytes`
objects never had the optimization in the first place: `b += b'x'` always
allocates and copies.
Both versions are $\Theta(n^2)$.

Compare against `concat_bytearray`.
A `bytearray` is mutable and deliberately allocates more room than it
currently needs, which is the same trick that makes `list.append` fast.
It does not care how many references point at it.

In `NOTES.md`: of the four ways to build up a sequence of bytes in this file,
which one would you actually use, and why is it the only one whose speed does
not depend on something invisible?

### 2b: free threading, and the GIL

Up to now, every python you have ever used has had a **global interpreter
lock**, or GIL: a single lock that guarantees only one thread is executing
python bytecode at a time.
The GIL is why python threads do not give you a speedup on CPU-bound work.
It is also what makes reference counting cheap: because only one thread can be
running, CPython can increment and decrement those counts with ordinary
non-atomic machine instructions.

Python 3.13 added an official build with no GIL, and 3.14 improved it.
That is the `3.14t` you installed.
Switch to it and check:
```
$ pyenv local 3.14t
$ python3 concat.py
```
The `gil =` line should say `False`.

Now re-run the two string rows:
```
$ python3 -m timeit -s 'import concat' 'concat.concat_fast(2**16)'
$ python3 -m timeit -s 'import concat' 'concat.concat_slow(2**16)'
```

|                     | 3.14 | 3.14t |
| ------------------- | ---- | ----- |
| `concat_fast`       |      |       |
| `concat_slow`       |      |       |

Record what you get.
Without a GIL, another thread could be adding or dropping a reference to your
string at the exact moment you check the count, so "the count is 1" stops
being a safe reason to believe that nobody else can see the buffer.
The free-threaded build also uses immortal and deferred reference counts for
some objects, which makes the number even less meaningful.

In `NOTES.md`: based on your measurements, does the free-threaded build still
have the in-place optimization?
Then answer the general question: you have now seen the same loop be fast or
slow depending on an unrelated assignment, on the scope the variable lives in,
and on which build of python you are running.
What should you conclude about writing `s += x` in a loop?

## Part 3: fitting the exponent with bigO

`timeit` gives you one number per cell.
To *identify* an asymptotic class you need a sweep and a fit.
The `bigO` package does this:
```
$ pip3 install -r requirements.txt
```

`bigO` works by decorating a function with `@bigO.track`, where the argument
is a function that computes the size of the input:
```python
@bigO.track(lambda pair: len(pair[0]))
def find_adversarial(pair):
    return algorithms.find(pair)
```
Every call is recorded, and a fit over all the recorded calls is produced at
the end.

This is already written for you in `track.py`.
Run it under each version, then produce the report:
```
$ python3 track.py
$ python3 -m bigO
```
This writes `bigO.pdf` and `bigO_data.json`.
Rename them per version (`bigO-3.9.pdf`, and so on) so that you do not
overwrite one with the other.

Record the fitted exponent:

|                    | 3.9 | 3.14 |
| ------------------ | --- | ---- |
| `find_adversarial` |     |      |
| `find_random`      |     |      |
| `str_to_int`       |     |      |
| `int_to_str`       |     |      |

> **NOTE:**
> `bigO` reports a class like `O(n)` or `O(n**2)`.
> When it reports `O(n**k)`, report the `k`.
> `k=1.98` versus `k=1.01` is a far more honest thing to write down than
> `O(n**2)` versus `O(n)`, because it shows you how good the fit actually was.

> **NOTE:**
> Only these four rows get fitted.
> `sum_floats` is linear on both versions and fitting it will produce a
> confident looking curve that tells you nothing.
> A curve fitter will always return *a* curve.

> **HINT:**
> If `bigO` will not install on 3.9, use `fit.py` instead.
> Put your measurements in a csv file with columns `n` and `seconds`, then
> run `python3 fit.py mydata.csv`.
> It prints the exponent implied by each consecutive pair of measurements,
> plus a least squares fit over all of them.
> You should do this by hand for at least one row either way, because it is
> the version of this technique that you can use anywhere:
> if doubling `n` multiplies the runtime by $2^k$, the runtime is $n^k$.

You should find that the two int/string rows have *different* exponents on
3.14, even though they are inverses of each other and both got faster.
Part 4 explains why.

## Part 4: the master theorem

Answer all of the following in `NOTES.md`.

### 4a: recurrences

The master theorem solves recurrences of the form
$$T(n) = a\,T(n/b) + f(n)$$
with $a \ge 1$ and $b > 1$.

1. **Schoolbook multiplication.**
   To multiply two $b$-bit numbers, split each in half and multiply the four
   pairs of halves: $T(b) = 4T(b/2) + \Theta(b)$.  Solve it.

1. **Karatsuba multiplication.**
   With one algebraic trick, three half-sized multiplications suffice instead
   of four: $T(b) = 3T(b/2) + \Theta(b)$.  Solve it.
   This is the algorithm CPython uses for large `int` multiplication, on every
   version in this lab.

1. **`int(s)` on a huge string of digits.**
   Python 3.12 replaced the quadratic digit-by-digit loop with a
   divide-and-conquer algorithm: split the digit string in half, convert each
   half, and recombine with one big multiplication:
   $$T(d) = 2T(d/2) + \Theta(M(d))$$
   where $M(d)$ is the cost of multiplying two $d$-digit numbers.
   Solve this twice: once with $M(d) = \Theta(d^2)$ and once with
   $M(d) = \Theta(d^{\log_2 3})$.
   Which one matches the exponent you measured in Part 3?

1. **`str(x)` on a huge int.**
   This direction also became divide-and-conquer in 3.12, with the same
   recurrence, but it reaches a *different* multiplication routine: it goes
   through the `decimal` module, whose underlying C library multiplies using a
   number-theoretic transform, which is nearly linear rather than
   $d^{1.585}$.
   Use the same recurrence with $M(d) = \Theta(d \log d)$ and solve it.
   Does this explain why your two measured exponents differ?

1. **Substring search.**
   Write down the worst-case runtime of the simple search algorithm in terms
   of $n$ and $m$, and the worst-case runtime of the two-way algorithm.
   Then explain why the master theorem is of no use here at all.

### 4b: when the master theorem does not apply

Consider this recurrence, which comes from a real and famous problem:
$$T(n) = 2T(n-1) + O(1)$$

1. Solve it.  (It is not hard; expand it a few times and look at the pattern.)

1. Explain precisely why the master theorem cannot be used on it.
   State the precondition that it violates.

> **NOTE:**
> That recurrence is where the runtime of *catastrophic backtracking* comes
> from.  The regular expression `(a+)+$` matched against `'a'*n + 'b'` has no
> match, but the engine tries roughly $2^n$ different ways to split the run of
> `a`'s between the two quantifiers before it gives up.  Doubling `n` squares
> the runtime.
>
> Attacks that exploit this are called ReDoS, and they have taken down real
> services (Stack Overflow in 2016, Cloudflare in 2019).
> Unlike every other slow thing in this lab, this one was *not* fixed by a new
> version of python: `(a+)+$` is still exponential on 3.14.
> You can avoid it by rewriting the pattern, by using the possessive
> quantifier syntax `(a++)+$` that python 3.11 added, or by using a different
> regex engine entirely (`re2`, Go's `regexp`, Rust's `regex`), which are
> built on a different algorithm with a $\Theta(nm)$ worst case.
>
> Why can't python just switch to that algorithm?  Because python's regex
> language includes backreferences and lookaround, and those features are not
> expressible in the faster algorithm at all.  The faster engines do not
> support them.  Contrast this with `str.find`, whose entire specification is
> "is this substring in there, and where" -- a specification that says nothing
> about *how*, which is exactly why 3.10 was free to replace the how.

### 4c: what does the $O(\cdot)$ notation protect you from?

Look at your two `sum` rows: the runtime row from Part 1a and the value rows
from Part 1b.

Write a paragraph.
The runtime stayed $\Theta(n)$ and the answer changed.
What does an asymptotic bound promise you, and what does it say nothing about?
Name all three things it is silent on that you saw in this lab.

Then answer: if you are writing code where the exact numeric answer matters --
a simulation, a financial calculation, the coefficients of a polynomial --
what does this suggest about using `float`?
What could you use instead that would give you the same answer on every
version of python, forever?

## Submission

Commit the following to your fork:

- all tables from Parts 1, 2, and 3, filled in, with the `python3 -VV` output
  for each of your three installs recorded at the top
- `bigO.pdf` and `bigO_data.json` for each version (renamed so they do not
  collide)
- a `NOTES.md` with your written answers to Parts 1, 2, and 4

Submit the url to canvas.
