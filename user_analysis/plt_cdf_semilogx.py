#!/usr/bin/python

import sys
import matplotlib.pyplot as plt
import string


color = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
#labels = ['Client-to-ISP RTT', 'ISP-to-Server RTT']
#labels = ['mmsns', 'short', 'chat pictures and videos', 'chat messages']
#labels = ['WeChat user packets']
labels = ['total_bytes', 'pictures and videos upload bytes', 'chat pics download bytes', 'mmsns download bytes', \
        'xiaoxi upload bytes', 'xiaoxi download bytes', 'average active time']
def main(argv):
    for i in range(len(argv)-1):
        x = [float(_) for _ in open(argv[i+1])]
        x.sort()
        y = [1.*_/len(x)*100 for _ in range(len(x))]
        plt.semilogx(x, y, color[i])#, label=labels[i])
    # plt.xlim(0,1000)
    # plt.xlabel('#(flow)')
    plt.xlabel('time (s)')
    plt.ylabel('CDF')
    # plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.grid()
    plt.show()    
        
if __name__ == '__main__':
    print len(sys.argv)
    main(sys.argv)
    
    # plot_fig(x, y, 'r-+', '')
    # plot_fig(x, y, 'b-*', '')
    # plot_fig(x, y, 'g-o', '')
    #plt.savefig(sys.argv[2])
