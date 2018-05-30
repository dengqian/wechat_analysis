#!/usr/bin/pythons

import sys
import dpkt
from struct import pack, unpack
import string
from dpkt import tcp, ip 

comp_dict = dict()

fake_eth = pack('b', 0x00) * 12 + pack('bb', 0x08, 0x00)
HDLC_FLAG = pack('b', 0x7e)
HDLC_ESCAPE = pack('b', 0x7d)
HDLC_STR1 = pack('bb', 0x7d, 0x5d)
HDLC_STR2 = pack('bb', 0x7d, 0x5e)
IP_FLAG = pack('bb', 0x45, 0x00)
VAN_COMP_PROTO = pack('b', 0x2d)
VAN_UNCOMP_PROTO = pack('b', 0x2f)
IP_PROTO = pack('b', 0x21)

# flag bits for what changed in a packet
NEW_C = 0x40
NEW_I = 0x20
NEW_S = 0x08
NEW_A = 0x04
NEW_W = 0x02
NEW_U = 0x01

SPECIAL_I = (NEW_S|NEW_W|NEW_U)       
SPECIAL_D = (NEW_S|NEW_A|NEW_W|NEW_U)
SPECIALS_MASK = (NEW_S|NEW_A|NEW_W|NEW_U)

TCP_PUSH_BIT = 0x10
TCP_PUSH_FLAG = 0x0004 

TCP_PROTOCOL = pack('b', ip.IP_PROTO_TCP)

TIME_BASE = 0

comp_dict = dict()
class cstate:

    def __init__(self):
        self.ip= None
        self.tcp= None
        self.old_tcp = None
        self.old_ip = None
    
    def uncompress(self, data):
        if self.tcp == None:
            return ('', 0)
        pt = 0
        change = unpack("!H", data[pt:2])[0]
        change = (change & 0xff00) >> 8
        pt = pt + 1
        if change & NEW_C:
            ind = data[pt]
            pt = pt + 1

        if len(data[pt:]) >= 2:
            self.tcp.sum = unpack('!H', data[pt:pt+2])[0] & 0xffff
        else:
            return ('', 0)
        pt += 2

        if change & TCP_PUSH_BIT:
            self.tcp.flags |= tcp.TH_PUSH
        hdrlen = self.ip.hl * 4 + self.tcp.off * 4
        sc = change & SPECIALS_MASK
        if sc == SPECIAL_I:
            i = self.ip.len - hdrlen
            self.tcp.ack += i
            self.tcp.seq += i
        elif sc == SPECIAL_D:
            self.tcp.seq += self.ip.len - hdrlen
        else:
            if change & NEW_U:
                self.tcp.flags |= tcp.TH_URG
                x, pt = decode(data, pt)
                self.tcp.urp = x
            else:
                self.tcp.flags &= ~tcp.TH_URG
            if change & NEW_W:
                x, pt = decode(data, pt)
                if self.tcp.win + x < 65535:
                    self.tcp.win += x
            if change & NEW_A:
                x, pt = decode(data, pt)
                self.tcp.ack += x
            if change & NEW_S:
                x, pt = decode(data, pt)
                self.tcp.seq += x
        x = 0
        if change & NEW_I:
            x, pt = decode(data, pt)
            if self.ip.id + x < 65535:
                self.ip.id += x 
            else :
                self.ip.id += 1
        else:
            self.ip.id += 1
        self.ip.len += len(data[pt:])
        self.ip.len &= 0xffff
        self.ip.id &= 0xffff
        self.ip.sum = 0
        tmp_ip = self.ip
        tmp_tcp = self.tcp
        self.ip = self.old_ip
        self.tcp = self.old_tcp
        return str(tmp_ip)+str(tmp_tcp), pt 
        
def decode(data, pt):
    x = 0
    if len(data[pt:]) >= 2:
        x = unpack('!H', data[pt:pt+2])[0] 
        pt += 1
        if x & 0xff00 == 0:
            if len(data[pt+1:]) >= 2:
                x = unpack('!H', data[pt+1:pt+3])[0]
                pt += 2
        else:
            x &= 0xff
    elif len(data[pt:]) == 1:
        x = unpack('!H', data[pt-1:pt+1])[0]
        x &= 0x00ff
        pt += 1
    return (x, pt)

def init_vj_state(slot_id, piece):
    vj_state = cstate()
    vj_state.ip = ip.IP(piece[0:20]) 
    try:
        vj_state.tcp = tcp.TCP(piece[20:40]) 
    except:
        try:
            vj_state.tcp = tcp.TCP(piece[21:41]) 
        except:
           return 
    vj_state.old_tcp = vj_state.tcp
    vj_state.old_ip = vj_state.ip
    comp_dict[slot_id] = vj_state 


def unescape(data):
	return HDLC_ESCAPE.join([ HDLC_FLAG.join(d.split(HDLC_STR2)) for d in data.split(HDLC_STR1) ])
    
def decode_and_write(writer, pkt, ts):
    global TIME_BASE
    if TIME_BASE == 0:
        TIME_BASE = ts
    eth = dpkt.ethernet.Ethernet(pkt)
    ip = eth.data
    if ip.get_proto(ip.p) == dpkt.gre.GRE:
        gre_key = ip.data[4:8] # gre key
        data = ip.data[12:] # skip gre header
        
        begin = data.find(HDLC_FLAG)
        if begin > 0 and begin < len(data): # does not start with 7e
            data = data[begin+1:]

        while len(data) > 5 and data[0] == HDLC_FLAG:
            piece = ''
            data = data[1:]
            raw_data = data
            end = data.find(HDLC_FLAG)
#print ts-TIME_BASE, end
            if data[0] == VAN_UNCOMP_PROTO: # 7e2f
                piece = data[1:end-2]
                if len(piece) < 40:
                    piece = ''
                else:
                    slot_id = piece[9]+gre_key # slot_id in different flow can be the same
                    piece = piece[0:9]+TCP_PROTOCOL+piece[10:]
                    init_vj_state(slot_id, piece)
    
            elif data[0] == IP_PROTO:
                piece = data[1:end-2]
                piece = piece[0:9]+TCP_PROTOCOL+piece[10:]

            elif data[0] == VAN_COMP_PROTO:
                if data[2]+gre_key not in comp_dict:
                    piece = '' 
                else:
                    com = comp_dict[data[2]+gre_key]
                    data = data[1:end-2]
                    if len(data) >= 2:
                        piece, pt = com.uncompress(data)
                        piece += data[pt:]
            elif data[3] == IP_PROTO:
            	piece = data[4:end-2]

            elif data[3] == VAN_COMP_PROTO:
                if data[5]+gre_key not in comp_dict:
                    piece = ''
                else:
                    com = comp_dict[data[5]+gre_key]
                    data = data[4:end-2]
                    if len(data) >= 2:
                        piece, pt = com.uncompress(data)
                        piece += data[pt:]

            elif data[3] == VAN_UNCOMP_PROTO: # 7eff03002f
                piece = data[4:end-2]
                if len(piece) >= 40:
                    slot_id = piece[9]+gre_key
                    piece = piece[0:9]+TCP_PROTOCOL+piece[10:]
                    init_vj_state(slot_id, piece) 
                else:
                    piece = ''
            if piece == '':
                continue 
            if piece != '':
                new_pkt = fake_eth + unescape(piece)
                writer.writepkt(new_pkt, ts)
            begin = end + 1
            if begin >= len(raw_data):
               return 
            elif begin > 0:
               data = raw_data[begin:] 

if __name__ == '__main__':
	if len(sys.argv) < 2:
		sys.stderr.write('input & output PPP file is needed\n')
		sys.exit(-1)

	reader = dpkt.pcap.Reader(open(sys.argv[1], 'rb'))
	ofile = open(sys.argv[2], 'wb')
	writer = dpkt.pcap.Writer(ofile)

	for ts, pkt in reader:
	    try:	
                decode_and_write(writer, pkt, ts)
	    except:	
	        continue
	ofile.close()
