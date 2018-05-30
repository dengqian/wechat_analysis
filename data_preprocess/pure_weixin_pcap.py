#!/usr/bin/python
# coding: UTF-8

import sys
import dpkt
import struct
import socket

ip_dict = dict()
long_con_dict = dict()
    
def get_ip_dict(longip, ip_filename):
    for s in open(longip):
        long_con_dict[s[:-1]] = 1
    for s in open(ip_filename):
        if s.find(" ") == -1:
            long_con_dict[s[:-1]] = 1
        else:
            ip_dict[' '.join(s.split(' ')[0:2])] = 1

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
    key = '%s.%d %s.%d' % (src_ip, src_port, dst_ip, dst_port) 
    key1 = '%s.%d %s.%d' % (dst_ip, dst_port, src_ip, src_port) 
    del ip
    return (key, key1)

def handle_pcap(input_filename, output_filename):
    pcap = dpkt.pcap.Reader(open(input_filename))
    pcap_writer = dpkt.pcap.Writer(open(output_filename, 'wb'))
    for ts, pkt in pcap:
        ip = get_ip(pkt)
        if ip == None:
            del ts, pkt
            continue
        else:
            if ip[0] in ip_dict or ip[1] in ip_dict: 
                pcap_writer.writepkt(pkt, ts)
            elif ".".join(ip[0].split(".")[0:4]) in long_con_dict or ".".join(ip[1].split(".")[0:4]) in long_con_dict:
                pcap_writer.writepkt(pkt, ts)
        del ts, pkt

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage: <long ip file> <ip file> <input filename> <output filename>"
        sys.exit(-1)
    get_ip_dict(sys.argv[1], sys.argv[2])
    handle_pcap(sys.argv[3], sys.argv[4])
    del ip_dict
    del long_con_dict
