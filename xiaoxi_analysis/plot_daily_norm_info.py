#!/usr/bin/python

import sys
import matplotlib.pyplot as plt
import string
from collections import OrderedDict
import math
import bisect

# hash_table = dict()
N = len(sys.argv) - 1 
hash_table = [OrderedDict() for i in range(N)]
date = [1 * _ for _ in range(1,24)]
color = ['r-*', 'g-^', 'b-s']
#label = ['traffic flow distribution per day']
label = ['text messages','voice messages', 'emotion messages']
def plot_fig(x, y, col, lab):
    plt.plot(x, y, col, markeredgecolor=col[0], label=lab)
    # plt.xlim(1., 20000.)
    # plt.xlabel('')
    # plt.ylabel('CDF (%)')
    # plt.legend(loc='upper left')

def main(argv):
    for i in range(N):
        for s in open(argv[i+1]):
            ss = s.split(' ')
            try:
                ss[0] = bisect.bisect_left(date, float(ss[0]))
            except:
                print '!',ss[0]
            ss[1] = float(ss[1][:-1])
            if ss[0] not in hash_table[i]:
                hash_table[i][ss[0]] = ss[1]
                # print ss[0], ss[1]
            else:
                hash_table[i][ss[0]]= hash_table[i][ss[0]] + ss[1]
                # print ss[0]
        x = [k for k,v in hash_table[i].iteritems()]
        y = [v for k,v in hash_table[i].iteritems()]
        max_y = max(y)
        min_y = min(y)
        yy = [(ii-min_y)*1.0/(max_y-min_y) for ii in y]

        plot_fig(x, yy, color[i], label[i]) 
    
    plt.legend(loc='lower right')
    plt.grid()
    plt.show()    

if __name__ == '__main__':
    main(sys.argv)
