#!/usr/bin/python

import sys
from matplotlib import pyplot as plt
import numpy
import bisect
from scipy.interpolate import spline

def main(file1):
    data = [float(s) for s in open(file1)]
    minx = 0
    maxx = max(data) 
    step = 1
    x = numpy.arange(minx, maxx, step)
    all_y, all_edges = numpy.histogram(data , bins=(maxx-minx)/step, range=(minx, maxx))
    for _, it in enumerate(all_y):
        print it, _
    
    plt.bar(all_edges[:-1], all_y, width=1, color='#F0F8FF', edgecolor='#5F9EA0')
    plt.xlabel('Finish time(s)')
    plt.ylabel('Uncompleted rate')
    plt.xscale('log')
    plt.grid()
    plt.show()


if __name__ == '__main__':
    main(sys.argv[1])
