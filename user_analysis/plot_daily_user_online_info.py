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
# date = [10 * _ for _ in range(1,24*6)]
date = [60 * _ for _ in range(1,24)]
color = ['r-*', 'g-^', 'b', 'c']
col = ['r', 'g', 'b', 'c']
labels = ['All users', 'WeChat users']

def main(argv):
    for i in range(len(argv)-1):
        for s in open(argv[i+1]):
            ss = s.split(' ')
            ss[0] = bisect.bisect_left(date, int(ss[0]))
            ss[1] = int(ss[1][:-1])
            if ss[0] not in cnt_table:
                cnt_table[ss[0]] = dict()
                cnt_table[ss[0]][ss[1]] = 1
            else:
                cnt_table[ss[0]][ss[1]] = 1 

        x = [k for k,v in cnt_table.iteritems()]
        y = [len(v) for k,v in cnt_table.iteritems()]
        print x
        print y
        # plt.plot(x, y, color[i], markeredgecolor=col[i], label=labels[i])
        cnt_table.clear()
    plt.xlim(0, 23)
    plt.xlabel('time (hour)')
    plt.ylabel('#(users)')
    plt.legend(loc='upper left')
    plt.grid()
    plt.show()    
    
if __name__ == '__main__':
    main(sys.argv)
