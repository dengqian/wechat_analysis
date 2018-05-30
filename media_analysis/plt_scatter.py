#!/usr/bin/python

import sys
import matplotlib.pyplot as plt
import string
import numpy as np
from scipy.stats.stats import pearsonr


color = ['r', 'g', 'b', 'c']

def main(filename):
    x = [int(_.split(' ')[0]) for _ in open(filename)]
    y = [int(_.split(' ')[1]) for _ in open(filename)]
    print pearsonr(x, y)
    plt.scatter(x, y, s=25)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlim(0, 1000)
    # plt.ylim(0, 100)
    max_x = max(x)
    x = np.linspace(0, 95) 
    plt.plot(x, x, color = 'g')
    plt.xlabel('#(media flow per user)')
    plt.ylabel('#(unfinished media flow)')
    # plt.xlabel('expected content length')
    # plt.ylabel('actual content length')
    # plt.legend(loc='lower right')
    plt.grid()
    plt.show()    
        
if __name__ == '__main__':
    main(sys.argv[1])
    
