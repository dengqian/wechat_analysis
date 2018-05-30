#!/usr/bin/python

import sys
import string

user_dict = dict()
ACTIVE_TIME_THRESH = 60*4

class user_info:
    def __init__(self):
        # bytes
        self.total_byte_size = 0
        self.weixinnum_up_byte_size = 0
        self.weixinnum_down_byte_size = 0
        self.xiaoxi_up_byte_size = 0
        self.xiaoxi_down_byte_size = 0
        self.total_pkt_cnt =  0
        self.mmsns_down_byte_size = 0
        self.short_up_bytes = 0
        self.short_down_bytes = 0
        # active_time
        self.last_active_time = 0
        self.active_start_time = 0
        self.first_active_time = 0
        self.active_time_list = list()
        # pkt_cnt
        self.xiaoxi_up_pkt_cnt = 0
        self.mmsns_down_pkt_cnt = 0
        self.weixinnum_up_pkt_cnt = 0
        self.weixinnum_down_pkt_cnt = 0
        self.xiaoxi_up_pkt_cnt = 0
        self.xiaoxi_down_pkt_cnt = 0
        self.short_up_pkt_cnt = 0
        self.short_down_pkt_cnt = 0
        # flow cnt
        self.short_flow_cnt = 0
        self.weixinnum_up_cnt = 0
        self.weixinnum_down_cnt = 0
        self.mmbiz_flow_cnt = 0
        self.mmsns_flow_cnt = 0
        self.flow_cnt = 0
        self.flow_list = list()

    def update_info_list(self, ss):
        self.flow_list.append(ss[-1][:-1])
        self.flow_cnt += 1
        if self.active_start_time == 0:
            self.active_start_time = float(ss[4])
            self.last_active_time = float(ss[4])
            self.first_active_time = float(ss[4])
        cur_list = None
        if ss[-1][:-1] == 'weixinnum':
            self.weixinnum_up_byte_size += int(ss[12])
            self.weixinnum_down_byte_size += int(ss[8])
            self.weixinnum_up_pkt_cnt += int(ss[14])
            self.weixinnum_down_pkt_cnt += int(ss[10])
            if int(ss[14]) > int(ss[10]):
                self.weixinnum_up_cnt += 1
            elif int(ss[10]) > int(ss[14]):
                self.weixinnum_down_cnt += 1
        elif ss[-1][:-1] == 'mmsns':
            self.mmsns_down_byte_size += int(ss[8])
            self.mmsns_down_pkt_cnt += int(ss[10])
            self.mmsns_flow_cnt += 1 
        elif ss[-1][:-1] == 'short.weixin':
            self.short_flow_cnt += 1
            self.short_up_bytes += int(ss[12])
            self.short_down_bytes += int(ss[8])
            self.short_up_pkt_cnt += int(ss[14])
            self.short_down_pkt_cnt += int(ss[10])
        elif ss[-1][:-1] == 'xiaoxi':
            self.xiaoxi_up_byte_size += int(ss[12])
            self.xiaoxi_down_byte_size += int(ss[8])
            self.xiaoxi_up_pkt_cnt += int(ss[14])
            self.xiaoxi_down_pkt_cnt += int(ss[10])
        elif ss[-1][:-1] == 'mp.weixin' or ss[-1][:-1] == 'mmbiz':
            self.mmbiz_flow_cnt += 1

        if float(ss[4]) - self.last_active_time > ACTIVE_TIME_THRESH:
            self.active_time_list.append(self.last_active_time - self.active_start_time)
            self.active_start_time = float(ss[4])
        self.total_byte_size += int(ss[21])
        self.total_pkt_cnt += int(ss[10]) + int(ss[14])
        self.last_active_time = float(ss[19])

    def print_user_info(self, key):
        if len(self.active_time_list) == 0:
            self.active_time_list.append(self.last_active_time - self.active_start_time)
        average_active_time = 0
        for i in self.active_time_list:
            average_active_time += float(i)
        average_active_time = average_active_time/len(self.active_time_list)
        # print 'user_id:%s,total_byte_size:%d,total_pkt_cnt:%d,short_flow_cnt:%d,weixinnum_up_byte_size:%d,\
        #         weixinnum_down_byte_size:%d,xiaoxi_up_byte_size:%d,xiaoxi_down_byte_size:%d,\
        #         short_up_bytes:%d,short_down_bytes:%s,mmsns_down_byte_size:%d,average_active_time:%.3f,\
        #         active_time_cnt:%d,first_active_time:%.3f,last_active_time:%.3f,xiaoxi_up_pkt:%d,\
        #         xiaoxi_down_pkt_cnt:%d,weixinnum_up_pkt_cnt:%d,weixinnum_down_pkt_cnt:%d,\
        #         short_up_pkt_cnt:%d,short_down_pkt_cnt:%d,mmsns_down_pkt_cnt:%d'\
        #         % (key,self.total_byte_size,self.total_pkt_cnt,self.short_flow_cnt,\
        #         self.weixinnum_up_byte_size,self.weixinnum_down_byte_size, \
        #         self.xiaoxi_up_byte_size, self.xiaoxi_down_byte_size,self.short_up_bytes,\
        #         self.short_down_bytes, self.mmsns_down_byte_size,average_active_time,\
        #         len(self.active_time_list), self.first_active_time, self.last_active_time, \
        #         self.xiaoxi_up_pkt_cnt,self.xiaoxi_down_pkt_cnt, self.weixinnum_up_pkt_cnt,\
        #         self.weixinnum_down_pkt_cnt ,self.short_up_pkt_cnt, self.short_down_pkt_cnt,\
        #         self.mmsns_down_pkt_cnt)
        print key,self.short_flow_cnt, self.weixinnum_up_cnt, self.weixinnum_down_cnt, self.mmsns_flow_cnt,\
                len(self.active_time_list),average_active_time, self.mmbiz_flow_cnt

def parse_info(filename):
    for s in open(filename):
        ss = s.split(' ')
        if ss[0] not in user_dict:
            user_dict[ss[0]] = user_info()
        user_dict[ss[0]].update_info_list(ss)
        
def print_user_info():
    for k,v in user_dict.iteritems():
        v.print_user_info(k)
if  __name__ == '__main__':
    parse_info(sys.argv[1]) #
    print_user_info()
