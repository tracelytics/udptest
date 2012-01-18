# Tracelytics UDP settings test script
#
# (c) 2012 Tracelytics, Inc.
#
import signal
import socket
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 14725

BASE_UDP_SIZE = 1024
UDP_SEND_SIZE = 65507
UDP_RECV_SIZE = (100*1024)
UDP_INCREMENT = 1024

TIMEOUT = 0.05 # UDP recv timeout in seconds

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT

# set up sockets
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
recv_sock.bind((UDP_IP, UDP_PORT))

# test SO_SNDBUF, SO_RCVBUF
pre = send_sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, UDP_SEND_SIZE)
post = send_sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
print "Set SO_SNDBUF from %d to %d" % (pre, post)
pre = recv_sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, UDP_RECV_SIZE)
post = recv_sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
print "Set SO_RCVBUF from %d to %d" % (pre, post)

class TimeoutException(Exception):
    pass

def _raise_timeout_exception(_,__):
    raise TimeoutException

def run_test():
    cur_size = BASE_UDP_SIZE
    failures = 0

    while True:
        send_sock.sendto('a'*cur_size, (UDP_IP, UDP_PORT))

        signal.signal(signal.SIGALRM, _raise_timeout_exception)
        signal.setitimer(signal.ITIMER_REAL, TIMEOUT)

        try:
            data, addr = recv_sock.recvfrom(cur_size)

            print "received size ", len(data)
        except TimeoutException, e:
            print "FAILED size ", cur_size
            failures += 1

        if failures > 4:
            break

        if cur_size == UDP_SEND_SIZE:
            break
        cur_size = cur_size + UDP_INCREMENT
        if cur_size > UDP_SEND_SIZE:
            cur_size = UDP_SEND_SIZE

    print
    print "REPORT"
    print "Reached %d / %d bytes" % (cur_size, UDP_SEND_SIZE)
    print "Failures: %d" % (failures,)

if __name__ == '__main__':
    run_test()
