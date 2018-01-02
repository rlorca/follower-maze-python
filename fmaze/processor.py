from typing import Generator

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

    def __init__(self, payload: bytes):
        self.payload = payload

        fields = payload.decode(Protocol.ENCODING).strip().split(Protocol.FIELD_SEPARATOR)
        self.sequence = int(fields[Protocol.MessageFieldPosition.SEQ])
        self.type = fields[Protocol.MessageFieldPosition.TYPE]
        self.id_from = self.get_at_index_or_none(fields, Protocol.MessageFieldPosition.FROM)
        self.id_to = self.get_at_index_or_none(fields, Protocol.MessageFieldPosition.TO)

    def __str__(self):
        return self.payload

    def __eq__(self, other):
        return self.payload == other.payload

    @staticmethod
    def get_at_index_or_none(target, index):
        if len(target) > index:
            return target[index]

class MessageHandler:
    """
    Interface to be extended by classes receiving protocol messages.
    """

    def handle_follow(self, msg):
        """

        """
        pass

    def handle_unfollow(self, msg):
        """

        """
        pass

    def handle_broadcast(self, msg):
        """

        """
        pass

    def handle_private_message(self, msg):
        """

        """
        pass

    def handle_status_update(self, msg):
        """

        """
        pass


class MessageProcessor:

    def __init__(self, handler: MessageHandler):
        self.queue = _MessageQueue()
        self.handler_map = {
            Protocol.MessageType.FOLLOW: handler.handle_follow,
            Protocol.MessageType.UNFOLLOW: handler.handle_unfollow,
            Protocol.MessageType.BROADCAST: handler.handle_broadcast,
            Protocol.MessageType.PRIVATE_MESSAGE: handler.handle_private_message,
            Protocol.MessageType.STATUS_UPDATE: handler.handle_status_update
        }

    def process_message(self, payload : bytes):
        """
        Process a message, according to the

        :param payload: raw message received from event source
        """

        # store the message first
        self.queue.push(Message(payload))

        # reprocess the queue now
        for m in self.queue.pop():
            logging.debug("Dispatching message %d", m.sequence)

            if m.type in self.handler_map:
                self.handler_map[m.type](m)
            else:
                logging.warn("Message type %s unknown", m.type)





class _MessageQueue:
    """
    A message queue that respects the order defined by the sequence field of the messages.
    """

    def __init__(self):
        self.messages = {}
        self.next_seq = Protocol.INITIAL_SEQ

    def push(self, message: Message):
        """
        Add a message to the queue.
        :param message: message to be queued
        """
        self.messages[message.sequence] = message

    def pop(self) -> Generator[Message, None, None]:
        """
        Pops all messages available that respect the sequence field.
        """
        while self.next_seq in self.messages:
            msg = self.messages.pop(self.next_seq)
            self.next_seq = self.next_seq + 1
            yield msg
