#!/usr/bin/python
# coding: UTF-8

import sys
import dpkt
import struct
import socket

HTTP_METHOD = ["POST", "GET", "PUT", "HEAD", "DELETE", "TRACE", "OPTIONS", "CONNECT", "PATCH"]
USER_AGENT = "User-Agent"
HOST = "Host:"
CONTENT = "Content-Type"
CACHE = "Cache-Control"
hashtable = dict()

class pkt_header_info:
    def __init__(self):
        self.method = ''
        self.host = ''
        self.user_agent = ''
        self.ctt_type = ''
        self.cache_control = ''
    def __str__(self):
        # return 'Method:%s\nHost:%s\nU-A:%s' % (self.method, self.host, self.user_agent)
        return '%s, Method:%s, %s, %s, %s' % (self.host, self.method,
                self.user_agent, self.ctt_type, self.cache_control)
def get_pkt_key(pkt):
    if len(pkt)<34:
        return None
    eth = dpkt.ethernet.Ethernet(pkt)
    if eth == None:
        eth = dpkt.ssl.SSL(pkt)
        if eth.type != dpkt.ssl.ethernet.ETH_TYPE_IP:
            return None
    elif eth.type != dpkt.ethernet.ETH_TYPE_IP:
        return None
    ip = eth.data
    try:
        src_ip = socket.inet_ntoa(ip.src)
        dst_ip = socket.inet_ntoa(ip.dst)
        tcp = ip.data
        src_port = tcp.sport
        dst_port = tcp.dport
    except:
        return None

    key = '%s.%d %s.%d' % (src_ip, src_port, dst_ip, dst_port) 
    key1 = '%s.%d %s.%d' % (dst_ip, dst_port, src_ip, src_port) 
    return (key, key1)

def handle_pcap(filename):
    pcap = dpkt.pcap.Reader(open(filename))
    for ts, pkt in pcap:
        key = get_pkt_key(pkt)
        if key == None:
            continue
        if key[0] in hashtable:
            ph = hashtable[key[0]]
        elif key[1] in hashtable:
            ph = hashtable[key[1]]
        else:
            ph = pkt_header_info()
            hashtable[key[0]] = ph
        for i in range(0, 8):
            http = pkt.find(HTTP_METHOD[i])
            if http != -1:
                le = pkt[http:].find('\n')
                if le != -1:
                    ph.method = pkt[http:http+le]
                else: ph.method = pkt[http:]
         
        host = pkt.find(HOST)
        if host != -1:
            le = pkt[host:].find('\n')
            if le == -1:
                ph.host = pkt[host:]
            else:
                ph.host = pkt[host:host+le]
        ua = pkt.find(USER_AGENT)
        if ua != -1:
            le = pkt[ua:].find('\n')
            if le == -1:
                ph.user_agent = pkt[ua:]
            else:
                ph.user_agent = pkt[ua:ua+le]
        con = pkt.find(CONTENT)
        if con != -1:
            le = pkt[con:].find('\n')
            if le == -1:
                ph.ctt_type = pkt[con:]
            else:
                ph.ctt_type = pkt[con:con+le]
        cc = pkt.find(CACHE)
        if cc != -1:
            le = pkt[cc:].find('\n')
            if le == -1:
                ph.cache_control = pkt[cc:]
            else:
                ph.cache_control = pkt[cc:cc+le]
def print_result():
    for k, v in hashtable.iteritems():
        print k, str(v)
if __name__ == '__main__':
    handle_pcap(sys.argv[1])
    print_result()
