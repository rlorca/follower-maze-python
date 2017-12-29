from fmaze.follow_graph import FollowNetwork
from fmaze.processor import MessageProcessor

class Peers:

    def __init__(self):
        self.peers = {}

    def register(self, peer_id, connection):
        self.peers[peer_id] = connection

    def deliver(self, peer_id, message):
        if peer_id in self.peers:
            self.peers[peer_id].send(message.encode())

    def broadcast(self, message):

        m = message.encode()
        for p in self.peers.values():
            p.send(m)

    def shutdown(self):
        for p in self.peers.values():
            p.close()


class State:

    def __init__(self):
        self.peers = Peers()
        self.follow_graph = FollowNetwork()
        self.processor = MessageProcessor(self.__handle_event)

    def register_connection(self, peer_id, connection):
        self.peers.register(peer_id, connection)

    def shutdown(self):
        self.peers.shutdown()

    def new_event(self, event):
        self.processor.process(event)

    def __handle_event(self, message):

        if message.type == 'F':
            self.follow_graph.follow(message.id_from, message.id_to)
            self.peers.deliver(message.id_to, message.payload)

        elif message.type == 'U':
            self.follow_graph.unfollow(message.id_from, message.id_to)

        elif message.type == 'B':
            self.peers.broadcast(message.payload)

        elif message.type == 'P':
            self.peers.deliver(message.id_to, message.payload)

        elif message.type == 'S':
            for p in self.follow_graph.followers(message.id_from):
                self.peers.deliver(p, message.payload)
        else:
            print("Unknown message type ", message.payload)
