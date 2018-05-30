#!/usr/bin/python

import sys
from matplotlib import pyplot as plt
import numpy
import bisect
from scipy.interpolate import spline

def main(file1):
    data = [float(s) for s in open(file1)]
    minx = 0
    maxx = 1
    step = 0.05
    x = numpy.arange(minx, maxx, step)
    y, edges = numpy.histogram(data, bins=(maxx-minx)/step,\
            range=(minx, maxx))
    bincenters = 0.5*(edges[1:]+edges[:-1])
    y = [it*1.0/sum(y) for it in y]
    plt.bar(edges[:-1], y, width=step, color='#F0F8FF', edgecolor='#5F9EA0')
    newx = numpy.linspace(edges[0], edges[-1], 300)
    power_smooth = spline(bincenters, y, newx)
    plt.plot(newx, power_smooth, color='#778899')
    plt.xlim(minx, maxx)
    # plt.xlabel('Finish time(s)')
    plt.xlabel('Uncompletion rate')
    plt.ylabel('Ratio')
    plt.grid()
    plt.show()


if __name__ == '__main__':
    main(sys.argv[1])
