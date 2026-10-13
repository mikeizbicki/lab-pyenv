#!/usr/bin/env python3
'''
Estimate the exponent k in t = c * n**k from a csv file of measurements.

Use this if the bigO package will not install on one of your pythons.
The csv file needs a header line and two columns: n and seconds.  For example:

    n,seconds
    8192,0.00213
    16384,0.00851

Two estimates are printed.  The doubling ratio is the one you can do in your
head: if doubling n multiplies the runtime by 2**k, then the runtime is n**k.
'''

import argparse
import csv
import math


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('csv_file')
    return p.parse_args()


def load(fname):
    with open(fname) as f:
        rows = list(csv.DictReader(f))
    return [(float(r['n']), float(r['seconds'])) for r in rows]


def least_squares_slope(points):
    '''
    The slope of the best fit line through the points on a log-log plot,
    which is the exponent k.
    '''
    xs = [math.log(n) for n, t in points]
    ys = [math.log(t) for n, t in points]
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den = sum((x - mean_x) ** 2 for x in xs)
    return num / den


def main():
    args = parse_args()
    points = sorted(load(args.csv_file))

    print('consecutive ratios:')
    for (n0, t0), (n1, t1) in zip(points, points[1:]):
        k = math.log(t1 / t0) / math.log(n1 / n0)
        print('  n {:>12g} -> {:<12g}  time x{:<8.3f}  k={:.3f}'
              .format(n0, n1, t1 / t0, k))

    print('least squares k = {:.3f}'.format(least_squares_slope(points)))


if __name__ == '__main__':
    main()
