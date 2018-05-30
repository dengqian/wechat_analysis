#!/usr/bin/python
# coding: UTF-8

import sys
import dpkt
import struct
import socket

WEIXIN = ["weixin","wx\.","qpic","wxapi","wxlogic"]
def get_pkt_key(pkt):
    eth = dpkt.ethernet.Ethernet(pkt)
    if eth == None:
        return
    if eth.type != dpkt.ethernet.ETH_TYPE_IP:
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
        return
    ip = eth.data 
    try: 
        if ip.p != dpkt.ip.IP_PROTO_UDP:
            del eth
            return 
        udp = ip.data
        dns = dpkt.dns.DNS(udp.data)
        if len(dns.qd) != 1:
            return
        if dns.qd[0].name.find("long.weixin") != -1:
            for i in range(0, len(dns.an)):
                print socket.inet_ntoa(dns.an[i].ip)
        del eth
        return
    except:
        return
#@profile
def handle_pcap(filename):
    pcap = dpkt.pcap.Reader(open(filename))
    for ts, pkt in pcap:
        flag = 0
        #for s in WEIXIN:
        #    flag = pkt.find(s)
        #    if flag != -1:
        #        key = get_pkt_key(pkt)
        #        if key != None:
        #            print key
        #        break
        #if flag == -1:
        check_dns_packet(pkt)

if __name__ == '__main__':
    handle_pcap(sys.argv[1])
