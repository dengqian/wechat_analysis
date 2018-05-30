#!/usr/bin/python

import sys
import string

type_dict = dict()

def get_flow_type_dict(filename):
    for s in open(filename):
        ss = s.split(' ')
        t = ss[2]
        if len(ss) > 4:
            #print ss
            if s[4].find('mmsns') != -1:
                t = 'mmsns'
            elif ss[4].find('short') != -1:
                t = 'short'
            elif ss[4].find('mmbiz') != -1:
                t = 'mmbiz'
        else:
            t = t[:-1]
        if ss[0] not in type_dict:
            type_dict[ss[0]] = t
def main(filename):
    for s in open(filename):
        ss = s.split(' ')
        if ss[2] in type_dict:
            print ' '.join(ss[0:-1]),type_dict[ss[2]]
        else:
            print s[:-1]

if __name__ == '__main__':
    get_flow_type_dict(sys.argv[1])
    main(sys.argv[2])

