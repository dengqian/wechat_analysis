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
long_con_dict = dict()
type_dict = dict()

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
    if src_ip in weixin_server:
        pd.key = '%s.%d' % (dst_ip, dst_port)
        pd.dir = STOC 
        pd.server_ip = src_ip
    elif dst_ip in weixin_server:
        pd.key = '%s.%d' % (src_ip, src_port)
        pd.dir = CTOS
        pd.server_ip = dst_ip
    else:
        return None

    key = '%s.%d %s.%d' % (src_ip, src_port, dst_ip, dst_port) 
    key1 = '%s.%d %s.%d' % (dst_ip, dst_port, src_ip, src_port) 
    pd.dict_key = (key, key1)
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
        self.stream_type = None
        self.total_pkt_cnt = 0
        self.date = 0
        self.finish_time = 0
        self.syn_rtt = 0
        self.flow_byte = 0
        self.tcp_state = None

    def update_state(self, pd, pkt):
        self.finish_time = pd.ts - self.time_base
        self.flow_byte += len(pkt)
        self.total_pkt_cnt += 1
        if self.stream_type == None:
            flag = 0

        if pd.flag == 'S':
            self.key = pd.key
            if self.time_base == 0:
                self.time_base = pd.ts
        
        if pd.flag == 'SA':
            self.syn_rtt = pd.ts - self.time_base
        if pd.flag == 'F' or pd.flag == 'R':
            self.tcp_state = TCP_CLOSED
            

    def print_conn_info(self):
        self.finish_time += self.syn_rtt
        print self.key, self.stream_type, self.flow_byte, self.finish_time, self.date
        
           
def parse_performance(pd, pkt):
    if pd.key not in hash_table and pd.flag == 'S':
        stat = stat_struct()
        stat.date = (pd.ts + 8*3600) % 86400 * 1.0 / 60 
        stat.key = pd.key
        if stat.key in type_dict:
            stat.stream_type = type_dict[stat.key]
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

def get_xiaoxi_ip_dict(ip_filename):
    for s in open(ip_filename):
        long_con_dict[s[:-1]] = 1

def get_flow_type_dict(type_file):
    for s in open(type_file):
        type_dict[s.split(' ')[0]] = s.split(' ')[1][:-1]


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
        get_xiaoxi_ip_dict(sys.argv[2])
        get_flow_type_dict(sys.argv[3])
        for ind, filename in enumerate(sys.argv):
            if ind > 3:
                handle_pcap(filename)    
    for k,v in hash_table.iteritems():
        v.print_conn_info()
  
