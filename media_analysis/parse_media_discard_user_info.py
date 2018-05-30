#!/usr/bin/python

import sys
import string

user_dict = dict()

def get_user_info(filename, filename1):
    for s in open(filename):
        # key = '.'.join(s.split(' ')[0].split('.')[:-1])
        key = '.'.join(s.split(' ')[0].split('.')[:-2])
        # print key
        if key not in user_dict:
            user_dict[key] = [1,0] 
        else:
            user_dict[key][0] += 1
    for s in open(filename1):
        # key = '.'.join(s.split(' ')[0].split('.')[:-1])
        key = '.'.join(s.split(' ')[0].split('.')[:-2])
        # print key
        if key not in user_dict:
            print 'wrong'
            #user_dict[key] = [1, 1]
        else:
            user_dict[key][1] += 1
def print_user_info():
    for key, val in user_dict.iteritems():
        print key, val[0], val[1]
if __name__ == '__main__':
    get_user_info(sys.argv[1], sys.argv[2])
    print_user_info()
