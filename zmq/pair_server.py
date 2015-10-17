import zmq

context = zmq.Context()
s = context.socket(zmq.PAIR)
s.bind("tcp://0.0.0.0:8888")

while True:
    msg = s.recv()
    s.send("Echo: " + msg)
    print "Echo: " + msg
