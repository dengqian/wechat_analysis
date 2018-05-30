#!/usr/bin/python
import sys
import string

user_dict = dict()
ACTIVE_TIME_THRESH = 60*3 
user_info_dict = dict()
def get_user_info_dict(filename):
    for s in open(filename):
        ss = s.split(' ')
        user_info_dict[ss[0]] = s[:-1]
class xiaoxi_info:
    def __init__(self):
        self.up_cnt = 0
        self.down_cnt = 0
    def update_xiaoxi_info(self, ss):
        self.up_cnt += int(ss[4])
        self.down_cnt += int(ss[5])
    def print_user_info(self, key):
        if key in user_info_dict:
            print user_info_dict[key],self.up_cnt,self.down_cnt


def parse_info(filename):
    for s in open(filename):
        ss = s.split(' ')
        if ss[0] not in user_dict:
            user_dict[ss[0]] = xiaoxi_info()
        user_dict[ss[0]].update_xiaoxi_info(ss)
        
def print_user_info():
    for k,v in user_dict.iteritems():
        v.print_user_info(k)

if  __name__ == '__main__':
    get_user_info_dict(sys.argv[1])
    parse_info(sys.argv[2])
    print_user_info()
