#!/usr/bin/python

import sys
import matplotlib.pyplot as plt
import string
import numpy as np

#colors = ['r^', 'gs', 'bo', 'y*']
colors = ['r', 'g', 'b', 'y']

# colormap = plt.cm.gist_ncar
# plt.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 1, 3)])
labels = ['Mmsns medias', 'Short flows', 'Instant medias', 'Instant messages']
# labels = ['All flows', 'Uncompleted flows']
def main(argv):
    for i in range(len(argv)-1):
        la = argv[i+1].split('.')[0]
        x = list()
        for _ in open(argv[i+1]):
            # if float(_) != 0:
            x.append(float(_))
        # x = [float(_) for _ in open(argv[i+1])]
        y = [1.*_/len(x)*100 for _ in range(len(x))]
        x.sort()
        plt.semilogx(x, y,colors[i], label=labels[i],linewidth=2.0)
        # plt.plot(x, y,colors[i],linewidth=2.0)
        # plt.text(axis[i][0], axis[i][1]+3*i-3, txt[i])
    # plt.xlabel('finish time(s)')
    plt.xlabel('Uncompleted flow size (Byte)')
    # plt.xlabel('number of new flows within flow transfer time')
    # plt.xlabel('Acked data bytes')
    # plt.xlabel('Uncompletion rate')
    # plt.xlabel('Transmission rate (Byte/s)')
    # plt.xlim(100, 1000000 )
    plt.ylabel('CDF')
    plt.legend(loc='best')
    plt.grid()
    plt.show()    
        
if __name__ == '__main__':
    print len(sys.argv)
    main(sys.argv)
    
