#!/usr/bin/python

import sys
import dpkt
import struct
import socket
import math
import numpy

media_dict = dict()
class media_info:
    def __init__(self):
        self.start_time = 0
        self.finish_time = 0
        self.info = None
        self.flow_cnt = 0
def get_media_dict(file1):
    for s in open(file1):
        ss = s.split(' ')
        m = media_info()
        m.start_time = float(ss[2])
        m.finish_time = float(ss[6])
        m.info = s[:-1]
        port = int(ss[0].split('.')[-1])
        if port != 80 and port != 8080 and port != 443:
            key = '.'.join(ss[0].split('.')[0:-1])
        else:
            key = '.'.join(ss[1].split('.')[0:-1])
        if key not in media_dict:
            media_dict[key] = list()
            media_dict[key].append(m)
        else:
            media_dict[key].append(m)

def update_media_dict(filename):
    for s in open(filename):
        ss = s.split(' ')
        key = '.'.join(ss[1].split('.')[0:-1])
        date = float(ss[4])
        if key in media_dict:
            for i, it in enumerate(media_dict[key]):
                # print key, i #date, it.start_time, it.start_time+it.finish_time
                if date>it.start_time and date < it.start_time+it.finish_time:
                    media_dict[key][i].flow_cnt += 1

def print_media_info():
    for key, item in media_dict.iteritems():
        #print len(item), item
        for it in item:
            print it.info, it.flow_cnt
def main(file1, file2):
    get_media_dict(file1) 
    update_media_dict(file2)
    print_media_info()
    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: <media info file> <all flow info file>'
    main(sys.argv[1], sys.argv[2])
