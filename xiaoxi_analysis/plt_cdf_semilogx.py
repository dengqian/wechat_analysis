#!/usr/bin/python

import sys
import matplotlib.pyplot as plt
import string


color = ['r', 'g', 'b']
#labels = ['Client-to-ISP RTT', 'ISP-to-Server RTT']
#labels = ['user active time']
labels = ['text', 'voice', 'emotions']

def main(argv):
    for i in range(len(argv)-1):
        x = [float(_) for _ in open(argv[i+1])]
        y = [1.*_/len(x)*100 for _ in range(len(x))]
        plt.semilogx(x, y, color[i], label=labels[i])
        # plt.plot(x, y, color[i], label=labels[i])
    # plt.xlim(0,1000)
    plt.xlabel('RTT ')
    plt.ylabel('CDF')
    plt.legend(loc='lower right')
    plt.grid()
    plt.show()    
        
if __name__ == '__main__':
    print len(sys.argv)
    main(sys.argv)
    
    # plot_fig(x, y, 'r-+', '')
    # plot_fig(x, y, 'b-*', '')
    # plot_fig(x, y, 'g-o', '')
    #plt.savefig(sys.argv[2])
