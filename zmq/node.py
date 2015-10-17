#!/usr/bin/env python

import zmq
import time
import traceback

class Peer:
    def __init__(self, serverport, myid=None, serverhost=None):
        self.debug = 0

        self.serverport = int(serverport)
        if serverhost:
            self.serverhost = serverhost
        else:
            self.serverhost = '0.0.0.0'

        if myid:
            self.myid = myid
        else:
            self.myid = "{0}:{1}".format(self.serverhost, self.serverport)

        self.peers = {}
        self.shutdown = False

        self.handlers = {}
        self.router = None


    def __handlepeer(self, clientsock):
        host, port = clientsock.getpeername()
        peerconn = PeerConnection(None, host, port, clientsock, debug=False)

        
    def makeserversocket(self, port, backlog=5):
        context = zmq.Context()
        s = context.socket(zmq.REP)
        s.bind("tcp:{host}:{port}".format(
            host=self.serverhost, port=self.serverport))
        
        return s

    def connectandsend(self, host, port, msg, pid=None, waitreply=True):

        msgreply = []
        
        try:
            peerconn = PeerConnection(pid, host, port, debug=True)
            peerconn.senddata(msg)
            print "Sent {0}: {1}".format(pid, msg)

            if waitreply:
                reply = peerconn.recvdata()
                while (reply != None):
                    msgreply.append(reply)
                    print "Got reply {0}: {1}".format(pid, str(msgreply))
                    reply = peerconn.recvdata()
                peerconn.close()
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()

        return msgreply

    def mainloop(self):

        s = self.makeserversocket(self.serverport)
        print "Server started: {0} ({1}:{2})".format(
            self.myid, self.serverhost, self.serverport)

        while not self.shutdown:
            try:
                print "Listening for connections..."
                message = sock.recv()
                sock.send("Echo: " + message)
                print "Echo: " + message
            except KeyboardInterrupt:
                print "KeyboardInterrupt: stopping mainloop"
                self.shutdown = True
                continue
            except:
                traceback.print_exc()
                continue

        print 'Main loop exiting'
        s.close()

class PeerConnection:
    def __init__(self, peerid, host, port, sock=None, debug=False):
        self.id = peerid

        if not sock:
            context = zmq.Context()
            self.s = context.socket(zmq.REQ)
            self.s.connect("tcp://{0}:{1}".format(host, port))
        else:
            self.s = sock

    def senddata(self, msg):
        try:
            self.s.send(msg)
            print "Sent: {}".format(msg)
        except KeyboardInterrupt:
            raise
        except:
            print traceback.print_exc()
            return False
        return True

    def recvdata(self):
        rep = self.s.recv()
        print "Received: {}".format(rep)

    def close(self):
        self.s.close()
        self.s = None
        

        

               
                                          
