#!/usr/bin/env python3
'''
Drive the three functions whose asymptotic class we want bigO to identify.

Run this file, then run `python3 -m bigO` to produce bigO.pdf.

The sweeps below are sized for the *slow* version of python.  If you are on a
version where these are fast, you may raise the upper limits to get a cleaner
fit; just use the same limits for both versions when you compare them.
'''

import bigO

import algorithms


@bigO.track(lambda pair: len(pair[0]))
def find_adversarial(pair):
    return algorithms.find(pair)


@bigO.track(lambda pair: len(pair[0]))
def find_random(pair):
    return algorithms.find(pair)


@bigO.track(lambda s: len(s))
def str_to_int(s):
    return algorithms.str_to_int(s)


@bigO.track(lambda x: len(str(x)))
def int_to_str(x):
    return algorithms.int_to_str(x)


def sweep_find():
    for n in range(8192, 131072 + 1, 8192):
        find_adversarial(algorithms.make_adversarial(n))
        find_random(algorithms.make_random(n))


def sweep_digits():
    for d in range(10000, 100000 + 1, 10000):
        s = algorithms.make_digits(d)
        str_to_int(s)


def sweep_bigint():
    for d in range(10000, 100000 + 1, 10000):
        x = algorithms.make_bigint(d)
        int_to_str(x)


if __name__ == '__main__':
    print('sweeping substring search...')
    sweep_find()
    print('sweeping str -> int...')
    sweep_digits()
    print('sweeping int -> str...')
    sweep_bigint()
    print('done; now run: python3 -m bigO')
