#!/usr/bin/python

import sys
import matplotlib.pyplot as plt
import string
from collections import OrderedDict
import math
import bisect

# hash_table = dict()
hash_table = OrderedDict()
cnt_table = OrderedDict()
date = [1 * _ for _ in range(1,24)]
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
        ss = s.split(' ')
        ss[0] = bisect.bisect_left(date, float(ss[0]))
        ss[1] = float(ss[1][:-1])
        if ss[0] not in hash_table:
            hash_table[ss[0]] = list()
            hash_table[ss[0]].append(ss[1])
            cnt_table[ss[0]] = 1
            # print ss[0], ss[1]
        else:
            hash_table[ss[0]].append(ss[1])
            cnt_table[ss[0]] = cnt_table[ss[0]] + 1
            # print ss[0]

    x = [k for k,v in hash_table.iteritems()]
    y = [v.cnt_table[k] for k,v in hash_table.iteritems()]
    print [(k,v) for k,v in hash_table.iteritems()]
    # print x
    # print y
    plot_fig(x, y, 'r', '')
    
if __name__ == '__main__':
    main(sys.argv[1])
