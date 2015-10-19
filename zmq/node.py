#!/usr/bin/env python

import zmq.green as zmq
import gevent
import time
import traceback
import md5
import base64

class Socket:

    CLIENT = zmq.REQ
    SERVER = zmq.REP
    ROUTER = zmq.ROUTER
    DEALER = zmq.DEALER
    
    context = zmq.Context()

    def __init__(self, host, port, socket_type):
        self.host = host
        self.port = port
        self.sock = self.context.socket(socket_type)

    def connect(self):
        self.

class Client(Socket):
    def __init__(self, target_host, target_port):
        if target_host: self.host = target_host
        else: self.host = '0.0.0.0'
            
        self.port = target_port

        self.sock = self.context.socket(zmq.REQ)

    def connect(self):
        self.sock.connect("tcp://{0}:{1}".format(self.host, self.port))

    def send(self, msg):
        self.sock.send(msg)

    def recv(self):
        self.sock.recv()

    def close(self):
        self.sock.close()

class Server(Socket):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = self.context.socket(zmq.REP)

    def bind(self):
        self.sock.bind("tcp://{0}:{1}".format(self.host, self.port))

    def send(self, msg):
        self.sock.send(msg)

    def recv(self):
        self.sock.recv()

    def close(self):
        self.sock.close()

class Proxy(Socket):
    def __init__(self, front_host, front_port, back_host, back_port):
        self.front_host = front_host
        self.front_port = front_port
        self.back_host = back_host
        self.back_port = back_port

        self.frontend = self.context.socket(zmq.ROUTER)
        self.backend = self.context.socket(zmq.DEALER)

    def bind_and_connect(self):
        self.frontend.bind("tcp://{0}:{1}".format(
            self.front_host, self.front_port))
        
        self.backend.connect("tcp://{0}:{1}".format(
            self.back_host, self.back_port))

    def register_poll(self):
        self.poller = zmq.Poller()
        self.poller.register(self.frontend, zmq.POLLIN)
        self.poller.register(self.backend, zmq.POLLIN)

    def poll(self):
        while True:
            socks = dict(self.poller.poll())

            if socks.get(self.frontend) == zmq.POLLIN:
                print "New message on ROUTER"
                message = self.frontend.recv_multipart()
                self.backend.send_multipart(message)
                print "Sent message from DEALER"
                
            if socks.get(self.backend) == zmq.POLLIN:
                print "New message on DEALER"
                message = self.backend.recv_multipart()
                self.frontend.send_multipart(message)
                print "Sent message from ROUTER"

class Peer:

    def __init__(self, server_host, server_port, frontend_host, frontend_port, backend_host, backend_port, my_id=None, max_peers=0):

        if my_id:
            self.my_id = my_id
        else:
            self.my_id = Peer.make_id()
            
        self.max_peers = int(max_peers)

        self.peers = {
            self.my_id: {
                "server_host": server_host,
                "server_port": server_port,
                "frontend_host": frontend_host,
                "frontend_port": frontend_port,
                "backend_host": backend_host,
                "backend_port": backend_port,
                "client_host": None,
                "client_port": None
            }
        }

        self.shutdown = False

        # A static endpoint for REP
        self.server = Server(
            host=self.peers[self.my_id]["server_host"],
            port=self.peers[self.my_id]["server_port"]
        )

        self.server.bind()

        # A static endpoint for ROUTER/DEALER
        self.proxy = Proxy(
            front_host=self.peers[self.my_id]['frontend_host'],
            front_port=self.peers[self.my_id]['frontend_port'],
            back_host=self.peers[self.my_id]['backend_host'],
            back_port=self.peers[self.my_id]['backend_port']
        )

        self.proxy.bind_and_connect()
        self.proxy.register_poll()

    @staticmethod
    def make_id():
        m = md5.new()
        m.update(str(time.time()))
        return base64.encodestring(m.digest())[:-3].replace('/', '$')

    def add_peer(self, frontend_host, frontend_port, peer_id=None):
        if peer_id == None:
            peer_id == Peer.make_id()
        else:
            peer_id = peer_id

        self.peers[peer_id] = {
            "frontend_host": frontend_host,
            "frontend_port": frontend_port
        }
    
    def connect_to(self, peer_id):
        """Connect to the proxy of the peer"""
        for id in self.peers:
            if id == peer_id:
                self.client = Client(
                    self.peers[peer_id]['frontend_host'],
                    self.peers[peer_id]['frontend_port']
                )
                self.client.connect()
        
            else:
                print "Couldn't find peer"

    def poll(self):
        self.proxy.poll()
        gevent.sleep(0)

    def start_server(self):
        while True:
            req = self.server.recv()
            print "[CLIENT]: {}".format(req)
            rep = raw_input("[You]: ")
            self.server.send(rep)
            gevent.sleep(0)

    def start_client(self):
        while True:
            req = raw_input("[You]: ")
            self.client.send(req)
            rep = self.client.recv()
            print "[SERVER]: {}".format(rep)
            gevent.sleep(0)

    def activate(self):
        gevent.joinall([
            gevent.spawn(self.poll),
            gevent.spawn(self.start_server),
            gevent.spawn(self.start_client)
        ])



        

               
                                          
