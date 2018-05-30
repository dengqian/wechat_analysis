#!/usr/bin/python

import sys
import matplotlib.pyplot as plt
import string
import numpy as np


# colormap = plt.cm.gist_ncar
# plt.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 1, 8)])
colors = ['r', 'g', 'b', 'c', 'y', 'k']
# labels = ['packet loss rate', 'ctos_packet_loss_rate', 'stoc_packet_loss_rate']
labels = ['syn_rtt', 'max_ctos_rtt', 'avg_ctos_rtt', 'max_stoc_rtt', 'avg_stoc_rtt']
# labels = ['user id', 'short flow', 'media upload flow', 'media download flow',\
#         #'mmsns download flow',\
#         'active times', 'average active time', 'mmbiz flow', 'chat message received', \
#         'chat message sent']
x = [list() for i in range(10)]
plist = [1, 2, 3, 4, 7, 8, 9]
def main(filename):
    for s in open(filename):
        ss = s.split(' ')
        for i in range(len(ss)):
            if float(ss[i]) != 0:
                x[i].append(float(ss[i]))
    for i in range(len(ss)):
        x[i].sort()
        y = [1.*_/len(x[i])*100 for _ in range(len(x[i]))]
        plt.semilogx(x[i], y, color = colors[i], label=labels[i])
    # plt.xlabel('# active times')
    # plt.ylabel('average active time(s)')
    plt.legend(loc='lower right')
    plt.grid()
    plt.show()    
        
if __name__ == '__main__':
    main(sys.argv[1])
    
