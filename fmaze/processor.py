
from .logger import create_logger

logging = create_logger(__name__)

class Protocol:
    INITIAL_SEQ = 1
    ENCODING = "UTF-8"
    SERVER_EVENT_PORT = 9090
    SERVER_PEER_PORT = 9099
    FIELD_SEPARATOR = "|"

    class MessageType:
        FOLLOW = 'F'
        UNFOLLOW = 'U'
        PRIVATE_MESSAGE = 'P'
        STATUS_UPDATE = 'S'
        BROADCAST = "B"

    class MessageFieldPosition:
        SEQ = 0
        TYPE = 1
        FROM = 2
        TO = 3


class Message:

    def __init__(self, payload):
        self.payload = payload

        fields = payload.decode(Protocol.ENCODING).strip().split(Protocol.FIELD_SEPARATOR)
        self.sequence = int(fields[Protocol.MessageFieldPosition.SEQ])
        self.type = fields[Protocol.MessageFieldPosition.TYPE]
        self.id_from = self.get_at_index_or_none(fields, Protocol.MessageFieldPosition.FROM)
        self.id_to = self.get_at_index_or_none(fields, Protocol.MessageFieldPosition.TO)

    def is_broadcast(self):
        return self.type == Protocol.MessageType.BROADCAST

    def is_private_message(self):
        return self.type == Protocol.MessageType.PRIVATE_MESSAGE

    def is_follow(self):
        return self.type == Protocol.MessageType.FOLLOW

    def is_status_update(self):
        return self.type == Protocol.MessageType.STATUS_UPDATE

    def is_unfollow(self):
        return self.type == Protocol.MessageType.UNFOLLOW

    def __str__(self):
        return self.payload

    def __eq__(self, other):
        return self.payload == other.payload

    @staticmethod
    def get_at_index_or_none(list, index):
        if len(list) > index:
            return list[index]
        else:
            None


class MessageHandler:
    """
    Interface to be extended by classes receiving protocol messages.
    """

    def handle_follow(self, payload, id_from, id_to):
        """

        :param payload: message to be delivered to the target
        :param id_from: user following
        :param id_to: user being followed
        """
        pass

    def handle_unfollow(self, id_from, id_to):
        """

        :param id_from: user cancelling the follow
        :param id_to: user being unfollowed
        """
        pass

    def handle_broadcast(self, payload):
        """

        :param payload: message being broadcasted
        """
        pass

    def handle_private_message(self, payload, id_to):
        """

        :param payload: message being delivered
        :param id_to: id of the message's recipient
        """
        pass

    def handle_status_update(self, payload, id_from):
        """

        :param payload: raw message
        :param id_from: id of the user updating its status
        """
        pass


class MessageProcessor:

    def __init__(self, handler):
        self.queue = _MessageQueue()
        self.handler = handler

    def process_message(self, payload):
        """
        Process a message, according to the

        :param payload: raw message received from event source
        """

        # store the message first
        self.queue.push(Message(payload))

        # reprocess the queue now
        for m in self.queue.pop():
            self._dispatch_message(m)


    def _dispatch_message(self, message):

        logging.debug("Dispatching message %d", message.sequence)

        if message.is_follow():
            self.handler.handle_follow(message.payload, message.id_from, message.id_to)

        elif message.is_unfollow():
            self.handler.handle_unfollow(message.id_from, message.id_to)

        elif message.is_broadcast():
            self.handler.handle_broadcast(message.payload)

        elif message.is_private_message():
            self.handler.handle_private_message(message.payload, message.id_to)

        elif message.is_status_update():
            self.handler.handle_status_update(message.payload, message.id_from)


class _MessageQueue:
    """
    A message queue that respects the order defined by the sequence field of the messages.
    """

    def __init__(self):
        self.messages = {}
        self.next_seq = Protocol.INITIAL_SEQ

    def push(self, message):
        """
        Add a message to the queue.
        :param message: message to be queued
        """
        self.messages[message.sequence] = message

    def pop(self):
        """
        Pops all messages available that respect the sequence field.
        """
        while self.next_seq in self.messages:
            msg = self.messages.pop(self.next_seq)
            self.next_seq = self.next_seq + 1
            yield msg
