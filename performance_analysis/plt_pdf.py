#!/usr/bin/python

import sys
from matplotlib import pyplot as plt
import numpy
import bisect
from scipy.interpolate import spline

def main(file1, file2):
    all_finish_time = [float(s) for s in open(file1)]
    uc_finish_time = [float(s) for s in open(file2)]
    minx = 0
    maxx = 150
    step = 5
    x = numpy.arange(minx, maxx, step)
    all_y, all_edges = numpy.histogram(all_finish_time, bins=30, range=(minx, maxx))
    uc_y, edges = numpy.histogram(uc_finish_time, bins=30, range=(minx, maxx))
    y = []
    for i in range(len(all_y)):
        # print all_y[i]
        if all_y[i] != 0:
                y.append(uc_y[i]*1.0/all_y[i])
        else:
            y.append(0)
    # print len(y), len(edges)
    # xx = numpy.arange(minx, maxx/step, 1)
    bincenters = 0.5*(edges[1:]+edges[:-1])
    plt.bar(edges[:-1], y, width=5, color='#F0F8FF', edgecolor='#5F9EA0')
    newx = numpy.linspace(edges[0], edges[-1], 300)
    power_smooth = spline(bincenters, y, newx)
    plt.plot(newx, power_smooth, color='#000000')
    plt.xlim(0, 150)
    plt.xlabel('Finish time(s)')
    plt.ylabel('Uncompleted rate')
    plt.grid()
    plt.show()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
