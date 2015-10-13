from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor, defer
from twisted.protocols.basic import LineReceiver


class ChatProtocol(LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.name = None
        self.state = "REGISTER"

    def connectionMade(self):
        self.sendLine("What's your name?")

    def connectionLost(self, reason):
        if self.name in self.factory.users:
            del self.factory.users[self.name]
            self.broadcastMessage("{} has left the channel.".format(self.name))

    def lineReceived(self, line):
        if self.state == "REGISTER":
            self.handle_REGISTER(line)
        else:
            self.handle_CHAT(line)

    def handle_REGISTER(self, name):
        if name in self.factory.users:
            self.sendLine("Name taken, please choose another!")
            return
        self.sendLine("Welcome, {}".format(name))
        self.broadcastMessage("{} has joined the channel.".format(name))
        self.name = name
        self.factory.users[name] = self
        self.state = "CHAT"

    def handle_CHAT(self, message):
        message = "[%s]>> %s" % (self.name, message)
        self.broadcastMessage(message)

    def broadcastMessage(self, message):
        for name, protocol in self.factory.users.iteritems():
            if protocol != self:
                protocol.sendLine(message)

class ChatFactory(Factory):
    """Handle all the nodes' connection"""
    def __init__(self):
        self.users = {}

    def buildProtocol(self, addr):
        return ChatProtocol(self)

class Node:
    """
    A node is a self-contain unit consist of a client and server

    1) The client will connect to a leader node
    2) The server will listen and broadcast everything within the network
    """
    def __init__(self, stop=None):
        self.Factory = ChatFactory
        self.reactor = reactor
        self.d = defer.Deferred()
        if stop:
            self.reactor.callLater(stop, self.stop)

    def listen(self, port):
        self.reactor.listenTCP(port, self.Factory())

    def run(self):
        self.reactor.run()

    def stop(self):
        self.reactor.stop()

class Organization:
    """
    An organization consists of several nodes, with one node as
    a leader

    1) All nodes' clients will be connected to the leader node
    2) Each node's server will listen and broadcast the content for
       other nodes to potentially connect to
    3) If a leader node's connection is dead, the organization will
       elect a second-tiered node with most connections and promote
       it to leader, forwarding all connections to that node
    """
    def __init__(self):
        self.nodes = []

    def create_leader(self):
        # elect first node now with intentionally kill the leader's reactor after 5 seconds
        leader_node = Node(5)
        leader_node.listen(8000)
        self.nodes.append(leader_node)

    def create_more_nodes(self):
        node_1 = Node()
        node_2 = Node()
        self.nodes.append(node_1)
        self.nodes.append(node_2)

    def activate(self):
        ports = [8001, 8002, 8003, 8004]

        #self.nodes[0].listen(ports[0])
        self.nodes[1].listen(ports[1])
        self.nodes[2].listen(ports[2])
        #self.nodes[3].listen(ports[3])

        for n in self.nodes:
            n.run()

if __name__ == '__main__':
    org = Organization()

    org.create_leader()
    org.create_more_nodes()
    org.activate()
