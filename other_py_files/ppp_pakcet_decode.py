#!/usr/bin/python
#coding : UTF-8

import sys
import dpkt
import string

filename = sys.argv[2]
f = open(filename, 'a')
wirter = dpkt.pcap.Writer(f)
ts_base = 0

def parsePackets(data, ts):
    eth_packet = dpkt.ethernet.Ethernet(data)
    ip_packet = eth_packet.data
    global ts_base
    if ts_base == 0:
        ts_base = ts
    if ip_packet.get_proto(ip_packet.p) == dpkt.gre.GRE:
        gre_packet = ip_packet.data
        hex_packet = ':'.join(x.encode('hex') for x in gre_packet)
        ppp = hex_packet.find('7e')
        ip = 0
        while(hex_packet[ppp+2:].find('7e') > 0 and hex_packet[ppp:].find('45:00') > 0):
            new_eth = data.encode('hex')[:28]
            ip = ppp + hex_packet[ppp:].find('45:00') 
            ppp = ip + hex_packet[ip:].find('7e')
            ip_pac = hex_packet[ip:ppp-6]
            if ip < ppp:
            	new_pkt = new_eth + ip_pac.replace(':', '')
            	new_pkt = new_pkt.decode('hex')
                if len(new_pkt) > 2000:
                    print "%f"  % (ts - ts_base)
            	wirter.writepkt(new_pkt, ts)



def decapsulate(filename):
	pcap = dpkt.pcap.Reader(open(filename))
	for ts, pkt in pcap:
		parsePackets(pkt, ts)
		
decapsulate(sys.argv[1])
