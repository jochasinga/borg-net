# borg-net
Inspired by [the Borg](https://en.wikipedia.org/wiki/Borg_(Star_Trek)), this is a simple demo for a concept of Grassroot Representative Networks I'll be speaking about at the Radical Networks Conference. http://radicalnetworks.org/about/index.html on October 25, 2015.

The code is not yet there and might not be at all in time for the conference, but it's just a POF implemented in [Twisted](https://twistedmatrix.com/trac/).

## Ideas
The idea is to explore a way of organizing grassroot communication using "amateur" networks to simulate political organizations to leverage information against a surveilling dictator, authority or military head of state. Instead of people electing *representatives* with political background and money to represent their voices, the representatives are dynamically elected based on information and group of people they have at hands.

## Concept
### Node
A **Node** is a self-contain unit consist of a client and a server that anyone can implement on a machine (computer, Raspberry Pi, virtual machine)
1. The client will connect to a leader node's server
2.  The server will listen and broadcast the communication between this node and the leader node to any prospective client to connect to.

### Org
An **Org** consists of several nodes, with one node as an assigned leader or representative. An organization takes care of all the housework between its tenant nodes, including electing a new node as a representative when the former's connection is lost.
1. Each node's client will be connected to a leader node
2. Each node's server will start listening and broadcast the content between itself and the leader node to other prospective nodes to connect and vice versa.
3. If a leader node's connection is lost, the Org will elect a second-tiered node with the most number of connections and promote it to a representative, rerouting all connections from the former rep to the new one, and vice versa until there is no more node left in any tier of communication.

## TODO:
### Encryption
Each connection at every tier should be encrypted or tunneled to prevent surveillance by the ISP's gateway keepers (or better, TOR-rerouted).

### Data Distribution
Data storage should be distributed along the nodes (representatives) in the same tier, but at any point there must be a mechanism for each node to opt-in or -out to store data in an *Org* locally. In such a way that when an Org is compromised:
+ The representative may or may not have the information
+ Some nodes may or may not have the information
+ Information is copied to some connected representatives (No single point of vulnerability)

### Secure cloud storage
Also, instead of storing all data in the communication locally (in all or some nodes), there must be a way for any node to decide to securely upload to a decentralized, provider-independent cloud database, for instance, [Tahoe-LAFS](https://tahoe-lafs.org/trac/tahoe-lafs).
