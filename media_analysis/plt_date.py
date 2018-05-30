#!/usr/bin/python

import sys
import matplotlib.pyplot as plt
import string
from collections import OrderedDict
import math
import bisect

cnt_list = [0 for _ in range (25)]
date = [1 * _ for _ in range(0,24)]
def plot_fig(x, y, col, lab):
    plt.plot(x, y, col, markeredgecolor=col[0], label=lab)
    # plt.xlim(1., 20000.)
    # plt.xlabel('')
    # plt.ylabel('CDF (%)')
    # plt.legend(loc='upper left')
    plt.grid()
    plt.show()    

def main(argv):
    for s in open(argv):
        ss = float(s[:-1])
        #print bisect.bisect_left(date, ss)
        cnt_list[bisect.bisect_left(date, ss)] += 1
    print len(date), len(cnt_list)
    print date
    print cnt_list
    plot_fig(date, cnt_list[1:], 'r', '')
    
if __name__ == '__main__':
    main(sys.argv[1])


