#!/usr/bin/python
# coding: UTF-8

import sys
import dpkt
import struct
import socket

long_ip_dict = dict()
xiaoxi_dict = dict()
    
def get_ip_dict(longip):
    for s in open(longip):
        long_ip_dict[s[:-1]] = 1

def get_xiaoxi_dict(xiaoxifile):
    for s in open(xiaoxifile):
        xiaoxi_dict[s[:-1]] = 1

def get_ip(pkt):
    try:
        eth = dpkt.ethernet.Ethernet(pkt)
    except:
        return None
    if eth.type != dpkt.ethernet.ETH_TYPE_IP:
        del eth
        return None
    ip = eth.data
    del eth
    try:
        tcp = ip.data
        src_ip = socket.inet_ntoa(ip.src)
        dst_ip = socket.inet_ntoa(ip.dst)
        src_port = tcp.sport
        dst_port = tcp.dport
        del tcp
    except:
        del ip
        return None
    return (src_ip, src_port, dst_ip, dst_port)

def handle_pcap(input_filename, pcap_writer):
    pcap = dpkt.pcap.Reader(open(input_filename))
    for ts, pkt in pcap:
        ip = get_ip(pkt)
        if ip == None:
            del ts, pkt
            continue
        else:
            if ip[0] in long_ip_dict or ip[2] in long_ip_dict:
                pcap_writer.writepkt(pkt, ts)
            else :
                key = str(ip[0])+' '+str(ip[1])+' '+str(ip[2])+' '+str(ip[3])+' '
                if key in xiaoxi_dict:
                    pcap_writer.writepkt(pkt, ts)
                
        del ts, pkt

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage: <long ip file> <ip file> <input filename> <output filename>"
        sys.exit(-1)
    get_ip_dict(sys.argv[1])
    get_xiaoxi  
    pcap_writer = dpkt.pcap.Writer(open(sys.argv[2], 'wb'))
    for ind, filename in enumerate(sys.argv):
        if ind > 2:
            handle_pcap(sys.argv[ind], pcap_writer)
