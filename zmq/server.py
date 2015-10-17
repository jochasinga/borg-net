import zmq
import sys

context = zmq.Context()

sock = context.socket(zmq.REP)
sock.bind("tcp://0.0.0.0:8000")

while True:
    msg = sock.recv()
    sock.send("Echo: " + msg)
    print "Echo: " + msg
