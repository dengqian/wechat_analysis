#!/usr/bin/python

import sys
import dpkt
import struct
import socket
import math
import numpy
# from qqwry import *

__ts = [ 'TCP_LISTEN', 'TCP_SYN_RCVD', 'TCP_SYN_SENT', \
        'TCP_ESTABLISHED', 'TCP_FIN_SENT', 'TCP_FIN_1', \
        'TCP_FIN_RCVD', 'TCP_FIN_2', 'TCP_CLOSED', 'TCP_SERVER_CLOSED' ]
for s in __ts:
    exec("%s = '%s'" % (s, s))

weixin_server = dict()
hash_table = dict()
long_server = dict()

CTOS = "client_to_server"
STOC = "server_to_client"
TCP_OPEN = "TCP_OPEN"
TCP_DISORDER = "TCP_DISORDER"

G = 100
K = 4

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
    if src_ip in weixin_server and ( src_port == 80 or src_port == 8080 \
            or src_port == 443):
        pd.key = '%s.%d %s.%d' % (dst_ip, dst_port, src_ip, src_port)
        pd.dir = STOC 
        pd.server_ip = src_ip
    elif dst_ip in weixin_server and ( dst_port == 80 or dst_port == 8080 \
            or dst_port == 443):
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
        
        self.tcp_state = TCP_LISTEN 
        self.time_base = 0
        self.syn_dir = None
        self.server_ip = None
        self.stream_type = None
        self.finish_time = 0

        self.c_seq_sent = 0
        self.c_ack_sent = 0
        self.s_seq_sent = 0
        self.s_ack_sent = 0
        self.ctos_list = list()
        self.stoc_list = list()
        self.ctos_disorderd_list = list()
        self.stoc_disorderd_list = list()
        self.ctos_disorder_cnt = 0
        self.stoc_disorder_cnt = 0
        self.ctos_retrans_list = list() 
        self.stoc_retrans_list = list()
        
        self.syn_rtt = 0
        self.content_length = 0
        self.host = None
        self.rst_flag = None
        self.weixinnum_flag = None
        self.total_size = 0
        self.rst_dir = None
        self.data_dir = None
        self.syn_pkt_cnt = 0
        self.ctos_retrans_cnt = 0
        self.stoc_retrans_cnt = 0
        self.ctos_pkt_cnt = 0
        self.stoc_pkt_cnt = 0

        self.srtt_list = list()
        self.rttvar_list = list()
        self.srtt = 0
        self.rttvar = 0
        self.ctos_rtt_list = list()
        self.stoc_rtt_list = list()
        self.ctos_time_dict = dict()
        self.stoc_time_dict = dict()
        self.date = 0
        self.fin_flag = 0
        self.retrans_rate = 0
        # self.init_rwnd = 0
        # self.rwnd_scale = 0
        
    def update_state(self, pd, pkt):
        self.finish_time = pd.ts
        if self.host == None:
            host = pkt.find('Host:')
            if host != -1:
                end = pkt[host:].find('\r')
                self.host = pkt[host:host+end]
        if self.weixinnum_flag == None:
            wn = pkt.find('weixinnum')
            if wn != -1:
                self.weixinnum_flag = 'weixinnum'
        if pkt.find('qpic') != -1 or pkt.find('weixinnum') != -1:
            self.stream_type = 'needed'
        cl = pkt.find('CONTENT-LENGTH:')  
        if cl == -1:
            cl = pkt.find('Content-Length:')
        if cl != -1:
            le = pkt[cl:].find('\r')
            self.content_length = pkt[cl+16:cl+le]
            
        cl = pkt.find('totalsize')
        if cl != -1:
            self.total_size = pkt[cl+13:cl+18]
            if self.total_size == '':
                self.total_size = 0
        
        if pd.flag =='R':
            self.rst_flag = 'RST'
            self.tcp_state = TCP_CLOSED
            self.rst_dir = pd.dir
            return
                
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
                self.syn_dir = CTOS
                self.s_seq_base = pd.seq
                self.c_ack_base = pd.seq
                self.c_seq_base = pd.ack - 1
                self.s_ack_base = pd.ack - 1
            else:
                self.syn_dir = STOC
                self.c_seq_base = pd.seq
                self.s_ack_base = pd.seq
                self.s_seq_base = pd.ack - 1
                self.c_ack_base = pd.ack - 1
            self.syn_rtt = pd.ts - self.time_base
            self.tcp_state = TCP_SYN_RCVD

        if pd.dir == CTOS:
            if self.c_seq_base == 0:
                self.c_seq_base = pd.seq
                self.s_ack_base = pd.seq
            if self.s_seq_base == 0:
                self.s_seq_base = pd.ack - 1
                self.c_ack_base = pd.ack - 1
            # self.ctos_list.append((pd.seq-self.c_seq_base, pd.leng, pd.ack-self.c_ack_base, \
            #         '%.3f' % (pd.ts-self.time_base)))
            if self.tcp_state == TCP_SYN_RCVD and pd.seq == self.c_seq_base+1\
                    and pd.ack == self.c_ack_base+1:
                if self.syn_pkt_cnt == 2:
                    self.syn_rtt = pd.ts - self.time_base
                self.tcp_state = TCP_ESTABLISHED
            if pd.ack in self.stoc_time_dict and self.stoc_time_dict[pd.ack]!=0 and pd.flag != 'F' and pd.flag != 'R':
                self.stoc_rtt_list.append(pd.ts - self.stoc_time_dict[pd.ack])
                del self.stoc_time_dict[pd.ack]

            if pd.leng > 0:
                if pd.seq + pd.leng not in self.ctos_time_dict:
                    self.ctos_time_dict[pd.seq+pd.leng] = pd.ts
                else:
                    self.ctos_time_dict[pd.seq+pd.leng] = 0
                self.ctos_pkt_cnt += 1 
                # if pd.seq-self.c_seq_base>1 and pd.seq-self.c_seq_base <= self.c_seq_sent-1:
                #     self.ctos_retrans_cnt += pd.leng
                if pd.seq-self.c_seq_base >1 and pd.seq-self.c_seq_base != self.s_ack_sent :
                    self.ctos_disorderd_list.append((pd.seq-self.c_seq_base,\
                        pd.leng, pd.ack-self.c_ack_base))
                    if self.ctos_disorder_cnt >= 3 or len(self.ctos_disorderd_list) > 3 :
                        self.ctos_retrans_list.append((pd.seq-self.c_seq_base, pd.leng))
                        self.ctos_retrans_cnt += pd.leng
            elif pd.ack == self.c_ack_sent:
                self.stoc_disorder_cnt += 1
            if pd.ack >= self.s_seq_sent:
                self.stoc_disorder_cnt = 0

            
            self.c_seq_sent = max(self.c_seq_sent, pd.seq-self.c_seq_base+pd.leng)
            self.c_ack_sent = pd.ack-self.c_ack_base

            if pd.flag == 'F' and self.syn_dir == CTOS:
                self.fin_flag = 1
                self.tcp_state = TCP_FIN_1
            
            if self.tcp_state == TCP_SERVER_CLOSED:
                if pd.ack == self.s_seq_sent + 1:
                    self.tcp_state = TCP_CLOSED

        if pd.dir == STOC:
            if self.s_seq_base == 0:
                self.s_seq_base = pd.seq
                self.c_ack_base = pd.seq
            if self.c_seq_base == 0:
                self.c_seq_base = pd.ack - 1
                self.s_ack_base = pd.ack - 1
            # self.stoc_list.append((pd.seq-self.s_seq_base, pd.leng, pd.ack-self.s_ack_base,\
            #         '%.3f' % (pd.ts-self.time_base)))
            if self.tcp_state == TCP_SYN_RCVD and pd.seq == self.s_seq_base+1\
                    and pd.ack == self.s_ack_base+1:
                if self.syn_pkt_cnt == 2:
                    self.syn_rtt = pd.ts - self.time_base 
                self.tcp_state = TCP_ESTABLISHED
            if pd.ack in self.ctos_time_dict and self.ctos_time_dict[pd.ack] != 0 and pd.flag != 'F' and pd.flag != 'R':
                self.ctos_rtt_list.append(pd.ts - self.ctos_time_dict[pd.ack])
                del self.ctos_time_dict[pd.ack]

            if pd.leng > 0:
                if pd.seq+pd.leng not in self.stoc_time_dict:
                    self.stoc_time_dict[pd.seq+pd.leng] = pd.ts
                else:
                    self.stoc_time_dict[pd.seq+pd.leng] = 0
                self.stoc_pkt_cnt += 1
                # if pd.seq-self.s_seq_base>1 and pd.seq-self.s_seq_base <= self.s_seq_sent-1:
                #     self.stoc_retrans_cnt += pd.leng
                if pd.seq-self.s_seq_base>1 and (pd.seq-self.s_seq_base) != self.c_ack_sent:
                    self.stoc_disorderd_list.append((pd.seq-self.s_seq_base, \
                        pd.leng, pd.ack-self.s_ack_base))
                    if self.stoc_disorder_cnt >= 3:
                        self.stoc_retrans_list.append((pd.seq-self.s_seq_base, pd.leng))
                        self.stoc_retrans_cnt += pd.leng
            elif pd.ack == self.s_ack_sent:
                    self.ctos_disorder_cnt += 1

            if self.tcp_state == TCP_FIN_1 and pd.ack == self.c_seq_sent + 1:
                self.tcp_state = TCP_FIN_2

            if pd.flag == 'F':
                self.fin_flag = 1
                self.tcp_state = TCP_SERVER_CLOSED
                
            self.s_seq_sent = max(self.s_seq_sent, pd.seq-self.s_seq_base+pd.leng)
            self.s_ack_sent = pd.ack-self.s_ack_base

    def update_srtt(self, m):
        if m==0:
            m=1
        if self.srtt == 0:
            self.srtt = m*8
            self.rttvar = m*4
        else:
            m -= self.srtt/8
            self.srtt += m;
            
            if m<0 :
                m = -m
            self.rttvar += m
        self.srtt_list.append(self.srtt/8.0/1000)
        self.rttvar_list.append(self.rttvar/8.0/1000)

        # self.rto = self.srtt / 8 + max(G, K*self.rttvar)
        # print m, self.srtt, self.rttvar


    def print_conn_info(self):
        std_ctos_rtt = 0
        avg_ctos_rtt = 0
        std_stoc_rtt = 0
        avg_stoc_rtt = 0
        if len(self.ctos_rtt_list) > 0:
            avg_ctos_rtt = numpy.mean(self.ctos_rtt_list)
            std_ctos_rtt = numpy.std(self.ctos_rtt_list)
        if len(self.stoc_rtt_list) > 0:
            avg_stoc_rtt = numpy.mean(self.stoc_rtt_list)
            std_stoc_rtt = numpy.std(self.stoc_rtt_list)

        stoc_retrans_rate = 0
        ctos_retrans_rate = 0
        if self.stoc_retrans_cnt != 0:
            stoc_retrans_rate = self.stoc_retrans_cnt*1.0/(max(self.s_seq_sent, self.c_ack_sent)\
                    +self.stoc_retrans_cnt)
        if self.ctos_retrans_cnt != 0:
            ctos_retrans_rate = self.ctos_retrans_cnt*1.0/(max(self.c_seq_sent, self.s_ack_sent)\
                    +self.ctos_retrans_cnt)
        if self.stoc_retrans_cnt+self.ctos_retrans_cnt> 0:
            self.retrans_rate = (self.stoc_retrans_cnt+self.ctos_retrans_cnt)*1.0/\
                    (max(self.c_ack_sent, self.s_seq_sent) + max(self.s_ack_sent, self.c_seq_sent)\
                    +self.stoc_retrans_cnt+self.ctos_retrans_cnt) 
        

        if self.stream_type == 'needed':
            if self.ctos_pkt_cnt + self.stoc_pkt_cnt > 1 and self.c_ack_base != 0 and self.s_ack_base != 0:
                if self.s_seq_sent > self.c_seq_sent:
                    self.data_dir = 'download'
                else:
                    self.data_dir = 'upload'
                print self.key, self.date, self.weixinnum_flag, self.rst_flag, self.rst_dir,\
                    "%.4f" % (self.finish_time-self.time_base), self.data_dir,\
                    "%.6f" % self.retrans_rate,"%.6f" % ctos_retrans_rate, "%.6f" \
                    % stoc_retrans_rate,"%.4f" % self.syn_rtt, "%.4f" % std_ctos_rtt,\
                    "%.4f" % avg_ctos_rtt,"%.4f" % std_stoc_rtt, "%.4f" % avg_stoc_rtt,\
                    self.fin_flag, max(self.c_ack_sent, self.s_ack_sent), self.c_ack_base, self.s_ack_base,\
                    self.content_length, self.total_size
                # if self.s_seq_sent > self.c_seq_sent:
                #     self.data_dir = 'download'
                #     for rtt in self.stoc_rtt_list:
                #         self.update_srtt(int(rtt*1000))
                #     print self.key, self.date, self.data_dir, "%.4f" % std_stoc_rtt, "%.4f" % avg_stoc_rtt, \
                #             self.srtt, self.rttvar, self.fin_flag,\
                #             max(self.c_ack_sent, self.s_ack_sent), self.content_length
                # else:
                #     self.data_dir = 'upload'
                #     for rtt in self.ctos_rtt_list:
                #         self.update_srtt(int(rtt*1000))
                #     print self.key, self.date, self.data_dir, "%.4f" % std_ctos_rtt, "%.4f" % avg_ctos_rtt, \
                #             self.srtt, self.rttvar,  self.fin_flag,\
                #             max(self.c_ack_sent, self.s_ack_sent), self.content_length, self.total_size
                # try:
                #     self.content_length = int(self.content_length)
                # except:
                #     self.content_length = 0
                # if self.c_ack_sent >= self.content_length or self.s_ack_sent > self.content_length:
                #     fin_flag = 1
                # else:
                #     fin_flag = 0
                # if len(self.srtt_list) > 0 :
                #     print fin_flag, 'srtt', 'median:', numpy.median(self.srtt_list), 'max:', max(self.srtt_list), 'rttvar', 'median:', numpy.median(self.rttvar_list), 'max:', max(self.rttvar_list)
                # print ['%.4f' %  _ for _ in self.ctos_rtt_list]
                # print ['%.4f' % _ for _ in self.stoc_rtt_list]
            # print 'ctos_list', self.ctos_list
            # print 'ctos_disorderd_list', self.ctos_disorderd_list
            # print 'ctos_retrans_list', self.ctos_retrans_list
            # print 'stoc_list', self.stoc_list
            # print 'stoc_disorderd_list', self.stoc_disorderd_list
            # print 'stoc_retrans_list', self.stoc_retrans_list
    
def parse_performance(pd, pkt):
    if pd.key not in hash_table and (pd.flag == 'S' or pd.flag == 'SA'):
        stat = stat_struct()
        stat.date = pd.ts
        stat.key = pd.key
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

def handle_pcap(filename):
    pcap = dpkt.pcap.Reader(open(filename))
    for ts, pkt in pcap:
        if pkt == None:
            continue
        pd = get_pkt_desc(ts, pkt)
        if pd == None:
            continue
        parse_performance(pd, pkt)
        del pd
    
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: *.py <weixin_server_ip.txt> <pcap file>"
    else:
        get_weixin_ip_dict(sys.argv[1])
        for ind, filename in enumerate(sys.argv):
            if ind > 1:
                handle_pcap(filename)    
    for k,v in hash_table.iteritems():
        v.print_conn_info()
  
