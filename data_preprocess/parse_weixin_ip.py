#!/usr/bin/python
# coding: UTF-8

import sys
import dpkt
import struct
import socket


WEIXIN = ["weixinnum","short.weixin","mmsns","mmbiz","qpic","wx.qlogo","mp.weixin","wxlogic","weixin"]
def get_pkt_key(pkt):
    eth = dpkt.ethernet.Ethernet(pkt)
    if eth == None:
        return
    if eth.type != dpkt.ethernet.ETH_TYPE_IP:
        del eth
        return
    ip = eth.data 
    try:
        tcp = ip.data
        src_ip = socket.inet_ntoa(ip.src)
        dst_ip = socket.inet_ntoa(ip.dst)
        src_port = tcp.sport
        dst_port = tcp.dport
    except:
        del eth
        return None
    key = '%s.%d %s.%d' % (src_ip, src_port, dst_ip, dst_port) 
    del eth
    return key

def check_dns_packet(pkt):
    eth = dpkt.ethernet.Ethernet(pkt)
    if eth == None:
        return
    if eth.type != dpkt.ethernet.ETH_TYPE_IP:
        del eth
        return
    ip = eth.data 
    del eth
    try: 
        if ip.p != dpkt.ip.IP_PROTO_UDP:
            del eth
            return 
        udp = ip.data
        dns = dpkt.dns.DNS(udp.data)
        if dns.qd[0].name.find("long.weixin") != -1:
            for i in range(0, len(dns.an)):
                #print dns.qd[0].name,socket.inet_ntoa(dns.an[i].ip)
                print socket.inet_ntoa(dns.an[i].ip)
        del dns
        return
    except:
        return
#@profile
def handle_pcap(filename):
    pcap = dpkt.pcap.Reader(open(filename))
    for ts, pkt in pcap:
        flag = 0
        for s in WEIXIN:
            flag = pkt.find(s)
            if flag != -1:
                key = get_pkt_key(pkt)
                if key != None:
                    ho = pkt.find("Host")
                    if ho != -1:
                        le = pkt[ho:].find('\n')
                        print key, s, pkt[ho:ho+le]
                    else:
                        print key, s
                        break
        if flag != -1:
            check_dns_packet(pkt)
        del ts, pkt

if __name__ == '__main__':
    for filename in sys.argv:
        handle_pcap(sys.argv[1])
    #before = defaultdict(int)
    #after = defaultdict(int)
    #for i in get_objects():
    #    before[type(i)] += 1
    #for i in get_objects():
    #    after[type(i)] += 1
   
