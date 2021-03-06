from asyncore import dispatcher_with_send

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

    def register_connection(self, peer_id: str, connection: dispatcher_with_send):
        """
        Register a new peer connection
        """
        self.peers.register(peer_id, connection)

    def shutdown(self):
        """
        Terminate the execution.
        """
        self.peers.close_all()

    def handle_follow(self, msg):
        self.graph.follow(msg.id_from, msg.id_to)
        self.peers.deliver(msg.id_to, msg.payload)

    def handle_unfollow(self, msg):
        self.graph.unfollow(msg.id_from, msg.id_to)

    def handle_broadcast(self, msg):
        self.peers.broadcast(msg.payload)

    def handle_private_message(self, msg):
        self.peers.deliver(msg.id_to, msg.payload)

    def handle_status_update(self, msg):
        for p in self.graph.followers(msg.id_from):
            self.peers.deliver(p, msg.payload)


class _Peers:
    """
    Object that keeps track of connected peers.
     """

    def __init__(self):
        self.peers = {}

    def register(self, peer_id, connection: dispatcher_with_send):
        """
        Register a new peer
        """
        self.peers[peer_id] = connection

    def deliver(self, peer_id, message : bytes):
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

    def follow(self, follower_id : str, followee_id : str):
        if followee_id not in self.follow_map:
            self.follow_map[followee_id] = set()

        self.follow_map[followee_id].add(follower_id)

    def unfollow(self, follower_id : str, followee_id : str):
        return followee_id in self.follow_map and \
               self.follow_map[followee_id].discard(follower_id)

    def followers(self, followee_id : str):
        return frozenset(self.follow_map.get(followee_id, set()))
