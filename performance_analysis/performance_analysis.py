#!/usr/bin/python

import sys
import dpkt
import struct
import socket
import math
#from qqwry import *
from state_machine import *
_sm = state_machine()


weixin_server = dict()
hash_table = dict()
type_dict = dict()
long_server = dict()

CTOS = "client_to_server"
STOC = "server_to_client"
TCP_OPEN = "TCP_OPEN"
TCP_DISORDER = "TCP_DISORDER"

NO_SPU = 0
SPUR = 1

class pkt_desc:
    def __init__(self):
        self.ts = None
        self.key = None
        self.dir = None
        self.flag = None
        self.seq = None
        self.ack = None
        self.sack = None
        self.leng = 0
        self.server_ip = None
        self.dict_key = None

    def __str__(self):
        return 'ts = %.6lf, key = %s, dir = %7s, flag = %s, seq = %d, ack = %d, leng = %d' % \
            (self.ts, self.key, self.dir, self.flag, self.seq, self.ack, self.leng)

def get_pkt_desc(ts, pkt):
    try:
        eth = dpkt.ethernet.Ethernet(pkt)
    except:
        return None
    if eth.type != dpkt.ethernet.ETH_TYPE_IP:
        return None
    ip = eth.data
    
    if ip.p != dpkt.ip.IP_PROTO_TCP:
        return None
    try:
        tcp = ip.data
        src_ip = socket.inet_ntoa(ip.src)
        dst_ip = socket.inet_ntoa(ip.dst)
        src_port = tcp.sport
        dst_port = tcp.dport
    except:
        return None

    pd = pkt_desc()
    pd.ts = ts
    if src_ip in weixin_server and not (dst_port == 80 or dst_port==8080 or \
            dst_port==443):
        pd.key = '%s.%d %s.%d' % (dst_ip, dst_port, src_ip, src_port)
        pd.dir = STOC 
        pd.server_ip = src_ip
    elif dst_ip in weixin_server and not (src_port==80 or src_port==8080 or \
            dst_port==443):
        pd.key = '%s.%d %s.%d' % (src_ip, src_port, dst_ip, dst_port)
        pd.dir = CTOS
        pd.server_ip = dst_ip
    else:
        return None

    # flag
    pd.flag = 'A' # default A
    if tcp.flags & dpkt.tcp.TH_SYN:
        if tcp.flags & dpkt.tcp.TH_ACK:
            pd.flag = "SA"
        else:
            pd.flag = 'S'
    if tcp.flags & dpkt.tcp.TH_FIN:
        pd.flag = 'F'
    if tcp.flags & dpkt.tcp.TH_RST:
        pd.flag = 'R'

    # seq, ack, sack
    pd.seq = tcp.seq
    pd.ack = tcp.ack
         
    pd.leng = ip.len - ip.hl*4 - tcp.off*4

    return pd

class stat_struct:
    def __init__(self): # c:client_to_server pkt, s: server_to_client pkt
        self.key = None
        self.c_seq_base = 0
        self.c_ack_base = 0
        self.s_seq_base = 0
        self.s_ack_base = 0
        self.c_pkt_cnt = 0
        self.s_pkt_cnt = 0
        self.c_send_seg_size = 0
        self.s_send_seg_size = 0
        self.tcp_state = TCP_LISTEN 
        self.time_base = 0
        self.syn_rtt = 0
        self.syn_ack_rtt = 0
        self.syn_dir = None
        self.server_ip = None

        self.stream_type = None
        self.total_pkt_cnt = 0
        self.date = 0
        self.finish_time = 0
        self.c_seq_sent = 0
        self.c_ack_sent = 0
        self.s_seq_sent = 0
        self.s_ack_sent = 0
        self.ctos_disorderd_list = list()
        self.stoc_disorderd_list = list()
        self.ctos_disorder_cnt = 0
        self.stoc_disorder_cnt = 0
        self.ctos_retrans_list = list() 
        self.stoc_retrans_list = list()
        self.keep_alive_list = list()
        self.ctos_list = list()
        self.stoc_list = list()
        self.syn_pkt_cnt = 0
        self.end_time = 0
        self.flow_byte = 0
        self.fin_flag = None
        self.ctos_retrans_cnt = 0
        self.stoc_retrans_cnt = 0
        

    def update_state(self, pd, pkt):
        self.flow_byte += len(pkt)
        self.finish_time = pd.ts 
        self.total_pkt_cnt += 1
        self.end_time = pd.ts

        if pd.flag =='R':
            self.tcp_state = TCP_CLOSED
            self.fin_flag = 'RST'
            return
        if pd.flag == 'F':
            self.fin_flag = 'FIN'
        # if pd.flag == 'F' and self.syn_dir == None:
        #     self.tcp_state = TCP_CLOSED
        #     return 
                
        if pd.flag == 'S':
            self.syn_pkt_cnt += 1
            self.key = pd.key
            self.syn_dir = pd.dir
            if self.time_base == 0:
                self.time_base = pd.ts
            if pd.dir == CTOS:
                self.c_seq_base = pd.seq
                self.s_ack_base = pd.seq
            else :
                self.s_seq_base = pd.seq
                self.c_ack_base = pd.seq

            
        if pd.flag == 'SA':
            self.syn_pkt_cnt += 1
            if pd.dir == STOC:
                self.c_ack_base = pd.seq
                self.s_seq_base = pd.seq
                self.c_seq_base = pd.ack - 1
                self.s_ack_base = pd.ack - 1
            else:
                self.s_seq_base = pd.seq
                self.c_ack_base = pd.seq
                self.s_seq_base = pd.ack - 1
                self.c_ack_base = pd.ack - 1
            self.syn_rtt = pd.ts - self.time_base

        if pd.dir == CTOS:
            if self.c_seq_base == 0:
                self.c_seq_base = pd.seq
                self.s_ack_base = pd.seq
            if self.s_seq_base == 0:
                self.s_seq_base = pd.ack - 1
                self.c_ack_base = pd.ack - 1
            if self.tcp_state == TCP_SYN_RCVD and pd.seq == self.c_seq_base+1\
                    and pd.ack == self.c_ack_base+1:
                if self.syn_pkt_cnt == 2:
                    self.syn_ack_rtt = pd.ts - self.time_base - self.syn_rtt
            if pd.leng > 0:
                self.c_pkt_cnt += 1
                if pd.seq-self.c_seq_base>1 and (pd.seq-self.c_seq_base != self.s_ack_sent):
                    self.ctos_disorderd_list.append((pd.seq-self.c_seq_base,\
                        pd.leng, pd.ack-self.c_ack_base))
                    if self.ctos_disorder_cnt >= 3 or len(self.ctos_disorderd_list) > 3:
                        self.ctos_retrans_list.append((pd.seq-self.c_seq_base, pd.leng))
                        self.ctos_retrans_cnt += pd.leng
            elif pd.ack == self.c_ack_sent:
                    self.stoc_disorder_cnt += 1
            if pd.ack >= self.s_seq_sent:
                self.stoc_disorder_cnt = 0

            self.c_send_seg_size += pd.leng 
            # if pd.seq-self.c_seq_base == self.c_seq_sent-1 and pd.leng == 0: #     self.keep_alive_list.append((pd.seq-self.c_seq_base, \
            #         pd.ts-self.time_base))
            self.c_seq_sent = max(self.c_seq_sent, pd.seq-self.c_seq_base)
            self.c_ack_sent = max(self.c_ack_sent, pd.ack-self.c_ack_base)

        if pd.dir == STOC:
            if self.s_seq_base == 0:
                self.s_seq_base = pd.seq
                self.c_ack_base = pd.seq
            if self.c_seq_base == 0:
                self.c_seq_base = pd.ack - 1
                self.s_ack_base = pd.ack - 1

            if self.tcp_state == TCP_SYN_RCVD and pd.seq == self.s_seq_base+1\
                    and pd.ack == self.s_ack_base+1:
                if self.syn_pkt_cnt == 2:
                    self.syn_ack_rtt = pd.ts-self.time_base - self.syn_rtt

            if pd.leng > 0:
                self.s_pkt_cnt += 1
                if pd.seq-self.s_seq_base>1 and (pd.seq-self.s_seq_base) != self.c_ack_sent:
                    self.stoc_disorderd_list.append((pd.seq-self.s_seq_base, \
                        pd.leng, pd.ack-self.s_ack_base))
                    if self.stoc_disorder_cnt >= 3 or len(self.stoc_disorderd_list) > 3:
                        self.stoc_retrans_list.append((pd.seq-self.s_seq_base, pd.leng))
                        self.stoc_retrans_cnt += pd.leng
            elif pd.ack == self.s_ack_sent:
                self.ctos_disorder_cnt += 1
            if pd.ack >= self.c_seq_sent:
                self.ctos_disorder_cnt = 0
            self.s_send_seg_size += pd.leng 
            self.s_seq_sent = max(self.s_seq_sent, pd.seq-self.s_seq_base)
            self.s_ack_sent = max(self.s_ack_sent, pd.ack-self.s_ack_base)
            

            self.tcp_state = _sm.transit(self.tcp_state, pd.dir, pd.flag)


    def print_conn_info(self):
        self.finish_time = self.finish_time-self.time_base
        retrans_rate = 0
        # if self.s_seq_sent > self.c_seq_sent and self.stoc_retrans_cnt > 0:
        #     retrans_rate = self.stoc_retrans_cnt*1.0/(max(self.c_ack_sent, self.s_seq_sent)+\
        #            self.stoc_retrans_cnt)
        # elif self.ctos_retrans_cnt > 0:
        #     retrans_rate = self.ctos_retrans_cnt*1.0/(max(self.s_ack_sent, self.c_seq_sent)+\
        #            self.ctos_retrans_cnt)
        print "key:%s, date:%.1f, total:%d, server_send_seg_size:%d, s_pkt_cnt:%d,\
                client_send_seg_size:%d, c_pkt_cnt:%d, rtt:%f,flow_type:%s,\
                finish_time:%.3f, packect_loss_rate:%d, syn_dir:%s, end_time:%.1f, byte_size:%d, self.fin_flag:%s"\
                % (self.key,self.date, self.total_pkt_cnt, self.s_send_seg_size, self.s_pkt_cnt,\
                self.c_send_seg_size, self.c_pkt_cnt,self.syn_rtt+self.syn_ack_rtt, \
                self.stream_type, self.finish_time,retrans_rate\
                ,self.syn_dir, self.end_time, self.flow_byte, self.fin_flag)
        # print 'ctos_list:', self.ctos_list
        # print self.ctos_retrans_list
        # print 'stoc_list:', self.stoc_list
        # print self.stoc_retrans_list
    
def parse_performance(pd, pkt):
    if pd.key not in hash_table and (pd.flag == 'S' or pd.flag == 'SA'):
        stat = stat_struct()
        stat.date = pd.ts
        stat.key = pd.key
        stat.server_ip = pd.server_ip
        if stat.server_ip in long_server:
            stat.stream_type = 'xiaoxi'
        elif stat.key in type_dict:
            stat.stream_type = type_dict[stat.key]
        else:
            key = stat.key.split(' ')[1]+' '+stat.key.split(' ')[0]
            if key in type_dict:
                stat.stream_type = type_dict[key]
        stat.time_base = pd.ts
        hash_table[pd.key] = stat 
    elif pd.key not in hash_table:
        return

    stat = hash_table[pd.key]
    stat.update_state(pd, pkt)

    if stat.tcp_state == TCP_CLOSED:
        stat.print_conn_info()
        del hash_table[pd.key]
        return 

def get_weixin_ip_dict(weixinfile):
    for s in open(weixinfile):
        weixin_server[s[:-1]] = 1

def get_flow_type_dict(type_file):
    for s in open(type_file):
        ss = s.split(' ')
        if len(ss) > 1:
            key = ss[0]+' '+ss[1]
            t = ss[2]
            if len(ss) > 4:
                if ss[4].find('mmsns') != -1:
                    t = 'mmsns'
                elif ss[4].find('short') != -1:
                    t = 'short'
                elif ss[4].find('mmbiz') != -1:
                    t = 'mmbiz'
            elif t.find('\n') != -1:
                t = t[:-1]
            type_dict[key] = t

def get_long_dict(long_file):
    for s in open(long_file):
        long_server[s[:-1]] = 1

def handle_pcap(filename):
    pcap = dpkt.pcap.Reader(open(filename))
    for ts, pkt in pcap:
        if pkt == None:
            continue
        pd = get_pkt_desc(ts, pkt)
        if pd == None:
            continue
        parse_performance(pd, pkt)
    
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: *.py <weixin_server_ip.txt> <weixin_ip_type.txt> <pcap file>"
    else:
        get_weixin_ip_dict(sys.argv[1])
        get_flow_type_dict(sys.argv[2])
        get_long_dict(sys.argv[3])
        for ind, filename in enumerate(sys.argv):
            if ind > 3:
                handle_pcap(filename)    
    for k,v in hash_table.iteritems():
        v.print_conn_info()
  
