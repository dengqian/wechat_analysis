#!/usr/bin/python

CTOS = 'CTOS'
STOC = 'STOC'

__ts = [ 'TCP_LISTEN', 'TCP_SYN_RCVD', 'TCP_SYN_SENT', \
        'TCP_ESTABLISHED', 'TCP_LAST_ACK', 'TCP_FIN_1', \
        'TCP_CLOSE_WAIT', 'TCP_FIN_2', 'TCP_CLOSED', \
        'TCP_SERVER_CLOSED', 'TCP_CLOSING']
for s in __ts:
    exec("%s = '%s'" % (s, s))

class state_machine:
    def __init__(self):
        # cur_state + dir + flag -> nxt_state
        __s = list()
        ## 3-way handshake
        __s.append((TCP_LISTEN, CTOS, 'S', TCP_SYN_SENT))
        __s.append((TCP_SYN_SENT, STOC, 'SA', TCP_SYN_RCVD))
        __s.append((TCP_LISTEN, STOC, 'SA', TCP_SYN_RCVD))
        __s.append((TCP_SYN_SENT, CTOS, 'A', TCP_ESTABLISHED))
        
        # during transmission
        __s.append((TCP_ESTABLISHED, CTOS, 'A', TCP_ESTABLISHED))
        __s.append((TCP_ESTABLISHED, STOC, 'A', TCP_ESTABLISHED))
        
        # end of connection
        __s.append((TCP_ESTABLISHED, CTOS, 'R', TCP_CLOSED))
        __s.append((TCP_ESTABLISHED, STOC, 'R', TCP_CLOSED))
    
        __s.append((TCP_ESTABLISHED, STOC, 'F', TCP_SERVER_CLOSED))
	__s.append((TCP_SERVER_CLOSED, CTOS, 'A', TCP_CLOSE_WAIT))
        __s.append((TCP_SERVER_CLOSED, CTOS, 'F', TCP_LAST_ACK))
        __s.append((TCP_CLOSE_WAIT, CTOS, 'F', TCP_LAST_ACK))
        __s.append((TCP_LAST_ACK, STOC, 'A', TCP_CLOSED))
        __s.append((TCP_ESTABLISHED, CTOS, 'F', TCP_FIN_1))
        __s.append((TCP_FIN_1, STOC, 'A', TCP_FIN_2))
        __s.append((TCP_FIN_1, STOC, 'F', TCP_CLOSED))
        __s.append((TCP_FIN_2, CTOS, 'F', TCP_CLOSED))

        # __s.append((TCP_ESTABLISHED, STOC, 'F', TCP_SYN_SENT))
        # __s.append((TCP_FIN_SENT, CTOS, 'A', TCP_FIN_1))
        # __s.append((TCP_FIN_1, CTOS, 'A', TCP_FIN_1))
        # __s.append((TCP_FIN_1, CTOS, 'F', TCP_FIN_RCVD))
        # __s.append((TCP_FIN_RCVD, STOC, 'A', TCP_CLOSED))

        # __s.append((TCP_ESTABLISHED, CTOS, 'R', TCP_CLOSED))
        # __s.append((TCP_FIN_SENT, CTOS, 'R', TCP_CLOSED))
        # __s.append((TCP_FIN_1, CTOS, 'R', TCP_CLOSED))

        self._sm = dict()
        for s in __s:
            if s[0] not in self._sm:
                self._sm[s[0]] = dict()
            self._sm[s[0]][(s[1],s[2])] = s[3]

    def transit(self, cur, dir, flag):
        try:
            return self._sm[cur][(dir,flag)]
        except KeyError:
            # log error
            return cur
