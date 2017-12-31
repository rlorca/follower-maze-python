from .processor import MessageHandler

from .logger import create_logger

logging = create_logger(__name__)

class State(MessageHandler):

    def __init__(self):
        self.peers = _Peers()
        self.graph = _FollowNetwork()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    def register_connection(self, peer_id, connection):
        """
        Register a new peer connection
        """
        self.peers.register(peer_id, connection)

    def shutdown(self):
        """
        Terminate the execution.
        """
        self.peers.close_all()

    def handle_follow(self, payload, id_from, id_to):
        self.graph.follow(id_from, id_to)
        self.peers.deliver(id_to, payload)

    def handle_unfollow(self, id_from, id_to):
        self.graph.unfollow(id_from, id_to)

    def handle_broadcast(self, payload):
        self.peers.broadcast(payload)

    def handle_private_message(self, payload, id_to):
        self.peers.deliver(id_to, payload)

    def handle_status_update(self, payload, id_from):
        for p in self.graph.followers(id_from):
            self.peers.deliver(p, payload)


class _Peers:
    """
    Object that keeps track of connected peers.
     """

    def __init__(self):
        self.peers = {}

    def register(self, peer_id, connection):
        """
        Register a new peer
        """
        self.peers[peer_id] = connection

    def deliver(self, peer_id, message):
        """
        Deliver a message to the peer, if connected.
        """
        if peer_id in self.peers:
            self.peers[peer_id].send(message)

    def broadcast(self, message):
        """
        Broadcast a message to all connected peers.
        """
        for p in self.peers.values():
            p.send(message)

    def close_all(self):
        """
        Close connection to all peers.
        """
        logging.info("Closing %d peers", len(self.peers))

        for p in self.peers.values():
            p.close()


class _FollowNetwork:
    """
    A network of followers
    """

    def __init__(self):
        self.follow_map = {}

    def follow(self, follower_id, followee_id):
        """

        :param follower_id:
        :param followee_id:
        """
        if followee_id not in self.follow_map:
            self.follow_map[followee_id] = set()

        self.follow_map[followee_id].add(follower_id)

    def unfollow(self, follower_id, followee_id):
        """

        :param follower_id:
        :param followee_id:
        :return:
        """
        return followee_id in self.follow_map and \
               self.follow_map[followee_id].discard(follower_id)

    def followers(self, followee_id):
        """

        :param followee_id:  
        :return:
        """
        return frozenset(self.follow_map.get(followee_id, set()))
