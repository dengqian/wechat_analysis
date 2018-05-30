#!/usr/bin/python

import sys
import dpkt
import struct
import socket
import math
from collections import OrderedDict

__ts = [ 'TCP_LISTEN', 'TCP_SYN_RCVD', 'TCP_SYN_SENT', \
        'TCP_ESTABLISHED', 'TCP_FIN_SENT', 'TCP_FIN_1', \
        'TCP_FIN_RCVD', 'TCP_FIN_2', 'TCP_CLOSED', 'TCP_SERVER_CLOSED' ]
for s in __ts:
    exec("%s = '%s'" % (s, s))

hash_table = dict()
long_con_dict = dict()

CTOS = "client_to_server"
STOC = "server_to_client"

ACTIVE_TIME_THRESH = 180
OP_CODE = ['00000013', '000000ed', '00000044', '0000009b',\
        '00000038', '00000039', '0000022', '0000002c', '00000079',\
        '0000007a', '00000018', '00000012', '00000138', '0000006b', '00000009']


# OP_MEANING = ['voice messages', 'text messages', 'emotions', \
#         'get news', 'shake', 'shake', 'scan','add friends', 'open main pages',\
#         'server reply', 'server reply', 'server reply', 'change pages', 'forward pages']

OP_MEANING = ['voice messages', 'text messages', 'emotions', \
        'get news', 'shake', 'shake', 'scan','add friends', 'open main pages',\
        'server push or reply', '00000018', '00000012', '00000138', '0000006b', '00000009']
        
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
        self.op_code = None

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
    pd = pkt_desc()
    try:
        tcp = ip.data
        src_ip = socket.inet_ntoa(ip.src)
        dst_ip = socket.inet_ntoa(ip.dst)
        src_port = tcp.sport
        dst_port = tcp.dport
        if len(tcp) >= 20:
            data = tcp.data
            if len(data) > 0:
                if data[4:8].encode('hex') == '00100001':
                    pd.op_code = data[8:12].encode('hex')
    except:
        return None

    pd.ts = ts
    if src_ip in long_con_dict:
        pd.key = '%s.%d' % (dst_ip, dst_port)
        pd.dir = STOC 
        pd.server_ip = src_ip
    elif dst_ip in long_con_dict:
        pd.key = '%s.%d' % (src_ip, src_port)
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

    pd.leng = ip.len - ip.hl*4 - tcp.off*4

    return pd

class stat_struct:
    def __init__(self): # c:client_to_server pkt, s: server_to_client pkt
        self.key = None
        self.date = 0
        self.active_time_list = list()
        self.last_pkt_time = 0
        self.active_start_time = 0
        self.opcode_dict = dict()
        self.opcode_list = list()
        self.tcp_state = None
        self.pkt_time_list = list()
        self.up_opcode_cnt = 0
        self.down_opcode_cnt = 0
        self.time_list = list()

    def update_state(self, pd, pkt):
        # active_time
        if self.last_pkt_time != 0 and pd.ts - self.last_pkt_time > ACTIVE_TIME_THRESH:
            self.active_time_list.append((self.active_start_time, self.last_pkt_time))
            self.active_start_time = pd.ts

        # opcode 
        if pd.op_code != None:
            # pkt_time_list:packet arrival or send time  
            # self.pkt_time_list.append(pd.ts-self.time_base)
            self.time_list.append(pd.ts-self.time_base)
            self.opcode_list.append((pd.op_code, pd.ts-self.time_base, pd.dir))
            if pd.op_code in self.opcode_dict:
                self.opcode_dict[pd.op_code] += 1
            else:
                self.opcode_dict[pd.op_code] = 1
            if pd.op_code in OP_CODE:
                if pd.dir == STOC:
                    self.up_opcode_cnt += 1
                else :
                    self.down_opcode_cnt += 1

        self.last_pkt_time = pd.ts
        if pd.flag == 'F' or pd.flag == 'R':
            self.tcp_state = TCP_CLOSED
            return 
            

    def print_conn_info(self):
        if self.last_pkt_time > self.active_start_time:
            self.active_time_list.append((self.active_start_time, self.last_pkt_time))
        # print 'active_time', self.key, self.date, ['%.3f' % (it[1]-it[0]) for it in self.active_time_list]
        # print 'opcode_type_cnt', self.key, self.date, self.up_opcode_cnt, self.down_opcode_cnt 
        # print 'opcode_type_cnt',self.key, self.date, [(OP_MEANING[OP_CODE.index(k)],v) \
        #         if k in OP_CODE else (k, v) for k,v in self.opcode_dict.iteritems() ]
        # print self.key, self.date, [(OP_MEANING[OP_CODE.index(v[0])], v[1], v[2]) if v[0] in OP_CODE\
        #         else (v[0], v[1], v[2]) for v in self.opcode_list]
        # print 'time_list', self.key, self.date, [(v[0], '%.3f' % v[1], v[2]) for v in self.opcode_list]
        print [(v[0], '%.3f' % v[1], v[2]) for v in self.opcode_list]

           
def parse_performance(pd, pkt):
    if pd.key not in hash_table and (pd.flag == 'S' or pd.flag == 'SA'):
        stat = stat_struct()
        stat.time_base = pd.ts
        stat.active_start_time = pd.ts
        stat.key = pd.key
        stat.date = pd.ts 
        hash_table[pd.key] = stat 
    elif pd.key not in hash_table:
        return

    stat = hash_table[pd.key]
    stat.update_state(pd, pkt)

    if stat.tcp_state == TCP_CLOSED:
        if len(stat.opcode_dict) > 0:
            stat.print_conn_info()
        del hash_table[pd.key]
        return 

def get_xiaoxi_ip_dict(ip_filename):
    for s in open(ip_filename):
        long_con_dict[s[:-1]] = 1

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
    if len(sys.argv) < 2:
        print "Usage: <long_conn_ip.txt> <pcap file> <pcap file> ... "
    else:
        get_xiaoxi_ip_dict(sys.argv[1])
        for ind, filename in enumerate(sys.argv):
            if ind > 1:
                handle_pcap(filename)    
    for k,v in hash_table.iteritems():
        v.print_conn_info()
 
