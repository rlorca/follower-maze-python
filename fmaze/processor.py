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

    def __str__(self):
        return self.payload

    def __eq__(self, other):
        return self.payload == other.payload

    def get_at_index_or_none(self, list, index):
        if len(list) > index:
            return list[index]
        else:
            None


class MessageHandler:

    def handle_follow(self, payload, id_from, id_to):
        pass

    def handle_unfollow(self, id_from, id_to):
        pass

    def handle_broadcast(self, payload):
        pass

    def handle_private_message(self, payload, id_to):
        pass

    def handle_status_update(self, payload, id_from):
        pass


class MessageProcessor:

    def __init__(self, handler):
        self.queue = MessageQueue()
        self.handler = handler

    def process(self, payload):

        # store the message first
        self.queue.push(Message(payload))

        # reprocess the queue now
        for m in self.queue.pop():
            self.dispatch(m)

    def dispatch(self, message):

        if message.type == Protocol.MessageType.FOLLOW:
            self.handler.handle_follow(message.payload, message.id_from, message.id_to)

        elif message.type == Protocol.MessageType.UNFOLLOW:
            self.handler.handle_unfollow(message.id_from, message.id_to)

        elif message.type == Protocol.MessageType.BROADCAST:
            self.handler.handle_broadcast(message.payload)

        elif message.type == Protocol.MessageType.PRIVATE_MESSAGE:
            self.handler.handle_private_message(message.payload, message.id_to)

        elif message.type == Protocol.MessageType.STATUS_UPDATE:
            self.handler.handle_status_update(message.payload, message.id_from)


class MessageQueue:

    def __init__(self):
        self.messages = {}
        self.next_seq = Protocol.INITIAL_SEQ

    def push(self, message):
            self.messages[message.sequence] = message

    def pop(self):

        while self.next_seq in self.messages:
            msg = self.messages.pop(self.next_seq)
            self.next_seq = self.next_seq + 1
            yield msg