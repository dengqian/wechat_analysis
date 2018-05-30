#!/usr/bin/python

import sys
import dpkt
import struct
import re

type_dict = dict()

def get_flow_type_dict(type_file):
    for s in open(type_file):
        type_dict[s.split(' ')[0]] = s.split(' ')[1][:-1]

def main(filename):
    for s in open(filename):
        ss = re.split(':|,', s[:-1])
        key = ss[1]
        if key in type_dict:
            print ss[0:15],ss[18:],type_dict[key]

if __name__ == '__main__':
    get_flow_type_dict(sys.argv[1])
    main(sys.argv[2])
