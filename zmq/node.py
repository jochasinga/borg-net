#!/usr/bin/env python

import zmq.green as zmq
import gevent
import time
import traceback
import md5
import base64

class Socket:

    # socket_type
    CLIENT = zmq.REQ
    SERVER = zmq.REP
    ROUTER = zmq.ROUTER
    DEALER = zmq.DEALER

    # Central context/process
    context = zmq.Context()

    def __init__(self, host, port, socket_type):
        self.host = host
        self.port = port
        self.sock = self.context.socket(socket_type)

    def connect(self):
        self.sock.connect("tcp://{host}:{port}".format(self.host, self.port))

    def send(self, msg):
        self.sock.send(msg)

    def recv(self):
        self.sock.recv()

    def close(self):
        self.sock.close()

class Client(Socket):
    """Inherit the Socket class"""
    def __init__(self, target_port, target_host='0.0.0.0', socket_type=Socket.CLIENT):
        self.host = target_host
        self.port = int(target_port)
        self.sock = self.context.socket(socket_type)

class Server(Socket):
    """Inherit the Socket class"""
    def __init__(self, server_port, server_host='*', socket_type=Socket.SERVER):
        self.host = server_host
        self.port = int(server_port)
        self.sock = self.context.socket(socket_type)

    def bind(self):
        self.connect()

class Proxy(Socket):
    """
    Proxy is actually what other clients connect to, and it is always
    connected to the Node's server at the backend
    """
    def __init__(self, front_host, front_port, back_host, back_port):
        self.front_host = front_host
        self.front_port = int(front_port)
        self.back_host = back_host
        self.back_port = int(back_port)

        # Generate two sockets for front and back endpoints
        self.frontend = self.context.socket(Socket.ROUTER)
        self.backend = self.context.socket(Socket.DEALER)

    def connect(self):
        pass

    def send(self):
        pass

    def recv(self):
        pass

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

    def close(self):
        self.frontend.close()
        self.frontend.close()

class Peer:

    @staticmethod
    def make_id():
        """Make a md5-generated id for any unnamed peer"""
        m = md5.new()
        m.update(str(time.time()))
        return base64.encodestring(m.digest())[:-3].replace('/', '$')

    def __init__(self, server_host, server_port, frontend_host, frontend_port, backend_host, backend_port, my_id=None, max_peers=0):

        if my_id:
            self.my_id = my_id
        else:
            self.my_id = Peer.make_id()
            
        self.max_peers = int(max_peers)

        # Register myself as the first peer
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

        # A static endpoint for ROUTER/DEALER
        self.proxy = Proxy(
            front_host=self.peers[self.my_id]['frontend_host'],
            front_port=self.peers[self.my_id]['frontend_port'],
            back_host=self.peers[self.my_id]['backend_host'],
            back_port=self.peers[self.my_id]['backend_port']
        )

        self.proxy.bind_and_connect()
        self.proxy.register_poll()

        # A static endpoint for REP
        self.server = Server(
            host=self.peers[self.my_id]["server_host"],
            port=self.peers[self.my_id]["server_port"]
        )
        
        self.server.bind()

        # No client specified until a desire to connect
        self.client = None

        # Now ready for a poll loop

    def add_peer(self, peer_id, peer_host, peer_port):
        """
        You have to add peers first before connecting. 
        Right now there's no way of discovering peers yet.
        """
        peer_id = peer_id

        self.peers[peer_id] = {
            "frontend_host": peer_host,
            "frontend_port": int(peer_port)
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
                print "Couldn't find peer. Did you add him/her?"

    def poll(self):
        self.proxy.poll()
        gevent.sleep(0)

    def start_server(self):
        while True:
            req = self.server.recv()
            print "[SOMEONE]: {1}".format(req)
            rep = raw_input("[You]: ")
            self.server.send(rep)
            gevent.sleep(0)

    def start_client(self):
        while True:
            req = raw_input("[You]: ")
            self.client.send(req)
            rep = self.client.recv()
            print "[SOMEONE]: {}".format(rep)
            gevent.sleep(0)

    def activate(self):
        gevent.joinall([
            gevent.spawn(self.poll),
            gevent.spawn(self.start_server),
            gevent.spawn(self.start_client)
        ])

class Node(Peer):

    # default
    SERVER_HOST = '*'
    SERVER_PORT = 12345
    BACKEND_HOST = '0.0.0.0'
    BACKEND_PORT = 12346
    
    def __init__(self, frontend_host, frontend_port, server_host=SERVER_HOST, server_port=SERVER_PORT, backend_host=BACKEND_HOST, backend_port=BACKEND_PORT, my_id='john', max_peers=0):

        super(Node, self).__init__()

        """
        self.my_id = my_id
            
        self.max_peers = int(max_peers)

        # Register myself as the first peer
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

        # A static endpoint for ROUTER/DEALER
        self.proxy = Proxy(
            front_host=self.peers[self.my_id]['frontend_host'],
            front_port=self.peers[self.my_id]['frontend_port'],
            back_host=self.peers[self.my_id]['backend_host'],
            back_port=self.peers[self.my_id]['backend_port']
        )

        self.proxy.bind_and_connect()
        self.proxy.register_poll()

        # A static endpoint for REP
        self.server = Server(
            host=self.peers[self.my_id]["server_host"],
            port=self.peers[self.my_id]["server_port"]
        )
        
        self.server.bind()

        # No client specified until a desire to connect
        self.client = None

        """
    



        

               
                                          
