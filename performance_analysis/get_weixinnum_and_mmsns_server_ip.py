#!/usr/bin/python

import sys
import dpkt
import struct
import socket
import math
#from qqwry import *

__ts = [ 'TCP_LISTEN', 'TCP_SYN_RCVD', 'TCP_SYN_SENT', \
        'TCP_ESTABLISHED', 'TCP_FIN_SENT', 'TCP_FIN_1', \
        'TCP_FIN_RCVD', 'TCP_FIN_2', 'TCP_CLOSED', 'TCP_SERVER_CLOSED' ]
for s in __ts:
    exec("%s = '%s'" % (s, s))

weixin_server = dict()
hash_table = dict()
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
    if pd.key in type_dict:
        pd.stream_type = type_dict[pd.key]
        if pd.stream_type == 'weixinnum':
            print 'weixinnum', pd.server_ip
        if pd.stream_type == 'mmsns':
            print 'mmsns', pd.server_ip
    return pd

def get_weixin_ip_dict(weixinfile):
    for s in open(weixinfile):
        weixin_server[s[:-1]] = 1

def get_flow_type_dict(type_file):
    for s in open(type_file):
        type_dict[s.split(' ')[0]] = s.split(' ')[1][:-1]

def handle_pcap(filename):
    pcap = dpkt.pcap.Reader(open(filename))
    for ts, pkt in pcap:
        if pkt == None:
            continue
        pd = get_pkt_desc(ts, pkt)
    
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: *.py <weixin_server_ip.txt> <weixin_ip_type.txt> <pcap file>"
    else:
        get_weixin_ip_dict(sys.argv[1])
        get_flow_type_dict(sys.argv[2])
        for ind, filename in enumerate(sys.argv):
            if ind > 2:
                handle_pcap(filename)    
    # for k,v in hash_table.iteritems():
    #     v.print_conn_info()
  
