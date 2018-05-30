#!/usr/bin/python

import sys
import matplotlib.pyplot as plt
import numpy as np
import string
import matplotlib.cm as cm

#colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', '#']
# number = 17
# cmap = plt.get_cmap('gnuplot')
# colors = [cmap(i*10) for i in np.linspace(0, 1,number)]
# colors = cm.rainbow(np.linspace(0, 1, 100))
labels = ['total bytes','total packets','#(short flow)','chat and mmsns media upload bytes', 'chat media download bytes', \
        'xiaoxi upload bytes', 'xiaoxi download bytes','short_up_bytes','short_down_bytes','mmsns download bytes',\
        'average active time','#(active time)','first_active_time','last_active_time',\
        'xiaoxi upload packets','xiaoxi download packets','chat and mmsns media upload packets','chat media download packets', \
        'short upload packets', 'short download packets','mmsns media download packets']

x = [list() for i in range(len(labels))]
plist = [0,3,4,5,6,9,10,11]
# plist=[1,2,14,15,16,17,20]
colormap = plt.cm.gist_ncar
plt.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 1, 9)])
#plist = [0,2,3,4,5,6,7,8,11,12,13,14,15,16]
def main(argv):
    for i in range(len(argv)-1):
        for s in open(argv[i+1]):
            ss = s.split(' ')
            for ii in range(len(ss)):
                x[ii].append(float(ss[ii]))
        y = [1.*_/len(x[0])*100 for _ in range(len(x[0]))]
        cnt = 0
        for i in range(len(labels)):
            print i
            x[i].sort()
            #print len(x[i]),len(y)
            if i in plist:
                plt.semilogx(x[i], y, label=labels[i])
                cnt = cnt + 1

    plt.ylabel('CDF')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.grid()
    plt.show()    
        
if __name__ == '__main__':
    print len(sys.argv)
    main(sys.argv)
    
