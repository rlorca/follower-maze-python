class Message:

    def __init__(self, payload):
        self.payload = payload
        fields = payload.strip().split('|')
        self.sequence = int(fields[0])
        self.type = fields[1]
        self.id_from = get_at_index_or_none(fields, 2)
        self.id_to = get_at_index_or_none(fields, 3)

    def __str__(self):
        return self.payload

    def __eq__(self, other):
        return self.payload == other.payload


class MessageProcessor:

    def __init__(self, handler):
        self.queue = MessageQueue()
        self.handler = handler

    def process(self, payload):

        # store the message first
        self.queue.push(Message(payload))

        # reprocess the queue now
        for m in self.queue.pop():
            self.handler(m)


class MessageQueue:

    def __init__(self):
        self.messages = {}
        self.next_seq = 1

    def push(self, message):
            self.messages[message.sequence] = message

    def pop(self):

        while self.next_seq in self.messages:
            msg = self.messages.pop(self.next_seq)
            self.next_seq = self.next_seq + 1
            yield msg


def get_at_index_or_none(list, index):
    if len(list) > index:
        return list[index]
    else:
        None