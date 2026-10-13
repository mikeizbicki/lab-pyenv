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

## Part 0: setup

You're going to need to edit this repo, so:
Fork this repo, clone the fork, and `cd` into it.

## Part 1: pyenv

The `pyenv` program lets you use several different versions of python at once.
It has two main applications:
1. installing the latest versions of python on any computer, even if you don't have admin (root) permissions;
2. using an old version of python to run certain projects that only work with old versions of python.

### Part 1a: installing pyenv

Install pyenv with the following command
```
$ curl pyenv.run | bash
```
> **NOTE:**
> Recall that:
> 1. the `curl` command downloads the contents of a webpage and prints it to stdout,
> 2. the `|` passes the stdout of the left program to the stdin on the right program.
> So what the command above does is download the contents of the `pyenv.run` webpage and run the commands in `bash` (i.e. the shell).
> This is a common idiom used for installing programs in the terminal.

If everything worked correctly, you should be able to run
```
$ pyenv versions
* system (set by /home/usertest/.pyenv/version)
```
You should see only one line that looks similar (but not identical) to the output above.
This is the standard system-wide install of python that you have been using throughout this class so far.

You will need two more versions of python for this lab: 3.9 and 3.14.
Install them with the following commands:
```
$ pyenv install 3.9
$ pyenv install 3.14
```
Each command takes about 1 minute to run.

Once they finish, you should see these versions listed in the output below.
```
$ pyenv versions
* system (set by /home/usertest/.pyenv/version)
  3.9.25
  3.14.8
```

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
$ python --version
Python 3.14.8
$ pyenv local 3.9
$ python --version
Python 3.9.25
```

### Part 1.b: match/case

Now lets verify that the installed versions actually behave differently.

The file `matchcheck.py` uses the `match` statement, which was added to the language in python 3.10.
`match` in other languages is often called `switch`,
and is a short-hand form of repeated if/else statements.

Take a look at the file:
```
$ cat matchcheck.py
```

And observe that we get a syntax error with python 3.9.
```
$ pyenv local 3.9
$ python3 matchcheck.py
```

But if you switch to python 3.14, the program works.
```
$ pyenv local 3.14
$ python3 matchcheck.py
```

## Part 2: python versions and runtimes

Newer versions of python don't just add new syntax to python.
They also change the runtimes.
Usually the runtimes get faster, but not always.

In this section of the lab we will empirically observe runtime performance between python 3.9 and 3.14.

The file `algorithms.py` contains the functions you will time.

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

## Part 2: aliasing, reference counts, and the GIL

This section is different from the rest of the lab.
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

## Submission

Commit the following to your fork:

- all tables from Parts 1, 2, and 3, filled in, with the `python3 -VV` output
  for each of your three installs recorded at the top
- `bigO.pdf` and `bigO_data.json` for each version (renamed so they do not
  collide)
- a `NOTES.md` with your written answers to Parts 1, 2, and 4

Submit the url to canvas.
