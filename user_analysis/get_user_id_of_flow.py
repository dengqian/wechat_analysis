#!/usr/bin/python

import sys
import string
import re

user_dict = dict()
class user:
    def __init__(self):
        self.start_time = 0
        self.end_time = 0
        self.user_id = None

def get_user_dict(user_file):
    uid = 0
    for s in open(user_file):
        ss = s.split(' ')
        u = user()
        u.start_time = ss[1][:-1]
        u.user_id = uid
        uid += 1
        if ss[0] not in user_dict:
            user_dict[ss[0]] = list()
            user_dict[ss[0]].append(u)
        else:
            user_dict[ss[0]].append(u)

def main(user_file, pfm_file):
    get_user_dict(user_file)
    for s in open(pfm_file):
        ss = s.split(' ') 
        key1 = '.'.join(ss[1].split('.')[0:-1])
        key2 = '.'.join(ss[2].split('.')[0:-1])
        # print key
        if key1 in user_dict:
            user_list = user_dict[key1]
        elif key2 in user_dict:
            user_list = user_dict[key2]
        else:
            print 'error', key1, key2
            continue
        ts = float(ss[4])
        i = 0
        while i<len(user_list) and ts>user_list[i].start_time :
            i = i+1
        u = user_list[i-1]
        print u.user_id, s[:-1]

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
