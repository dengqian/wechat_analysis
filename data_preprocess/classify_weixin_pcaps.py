#!/usr/bin/python
# coding: UTF-8

import sys
import dpkt
import struct
import socket


weixin_type = dict()
long_con_dict = dict()
WEIXIN = ["weixinnum","short.weixin","mmsns","mmbiz","qpic","mp.weixin","weixin","wx.qlogo", "wxlogic"]
    
def get_ip_dict(ip_filename):
    dict_index = 0
    for s in open(ip_filename):
        if len(s) < 25:
            long_con_dict[s[:-1]] = 1
        else:
            key = ' '.join(s.split(' ')[0:2])
            wx_type = s.split(' ')[2].split('\n')[0]
            if key not in weixin_type:
                weixin_type[key] = wx_type
            
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

def handle_pcap(input_filename):
    pcap = dpkt.pcap.Reader(open(input_filename))
    
    xiaoxi_writer = dpkt.pcap.Writer(open(input_filename.split('.')[0]+"-xiaoxi.pcap", 'wb'))
    writer_list = [dpkt.pcap.Writer(open(input_filename.split('.')[0]+"-"\
            +types+".pcap", 'wb')) for types in WEIXIN]
    for ts, pkt in pcap:
        ip = get_ip(pkt)
        if ip == None:
            continue
        else:
            #if ip[0] in weixin_type:
            #    writer_list[WEIXIN.index(weixin_type[ip[0]])].writepkt(pkt, ts)
            #elif ip[1] in weixin_type:
            #    writer_list[WEIXIN.index(weixin_type[ip[1]])].writepkt(pkt, ts)
            if ".".join(ip[0].split(".")[0:4]) in long_con_dict or \
                    ".".join(ip[1].split(".")[0:4]) in long_con_dict:
                xiaoxi_writer.writepkt(pkt, ts)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: <ip file> <input filename>"
        sys.exit(-1)
    get_ip_dict(sys.argv[1])
    handle_pcap(sys.argv[2])
    del long_con_dict
