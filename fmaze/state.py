from fmaze.processor import MessageHandler


class State(MessageHandler):

    def __init__(self):
        self.peers = Peers()
        self.follow_graph = FollowNetwork()

    def register_connection(self, peer_id, connection):
        self.peers.register(peer_id, connection)

    def shutdown(self):
        self.peers.shutdown()

    def handle_follow(self, payload, id_from, id_to):
        self.follow_graph.follow(id_from, id_to)
        self.peers.deliver(id_to, payload)

    def handle_unfollow(self, id_from, id_to):
        self.follow_graph.unfollow(id_from, id_to)

    def handle_broadcast(self, payload):
        self.peers.broadcast(payload)

    def handle_private_message(self, payload, id_to):
        self.peers.deliver(id_to, payload)

    def handle_status_update(self, payload, id_from):
        for p in self.follow_graph.followers(id_from):
                self.peers.deliver(p, payload)


class Peers:

    def __init__(self):
        self.peers = {}

    def register(self, peer_id, connection):
        self.peers[peer_id] = connection

    def deliver(self, peer_id, message):
        if peer_id in self.peers:
            self.peers[peer_id].send(message)

    def broadcast(self, message):
        for p in self.peers.values():
            p.send(message)

    def shutdown(self):
        for p in self.peers.values():
            p.close()


class FollowNetwork:

    def __init__(self):
        self.followMap = {}

    def follow(self, followerId, followeeId):

        if followeeId not in self.followMap:
            self.followMap[followeeId] = set()

        self.followMap[followeeId].add(followerId)

    def unfollow(self, followerId, followeeId):
        return followeeId in self.followMap and \
               self.followMap[followeeId].discard(followerId)

    def followers(self, followeeId):
        return self.followMap.get(followeeId, set())