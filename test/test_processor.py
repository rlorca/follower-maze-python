from unittest import TestCase

from unittest.mock import Mock, call

from fmaze.processor import MessageProcessor, Message


class TestProcessor(TestCase):

    messages = [ Message(m.encode("UTF-8")) for m in  ["1|P|32|56", "2|P|32|56", "3|P|32|56"]]

    ##messages = [Message("1|P|32|56"), Message("2|P|32|56"), Message("3|P|32|56")]

    def setUp(self):
        # handler that will be receiving the messages in order
        self.handler = Mock().handle
        self.processor = MessageProcessor(self.handler)

    def test_message_is_added_to_the_queue(self):
        self.processor.process(self.messages[1].payload)
        self.handler.assert_not_called()

    def test_message_is_delivered(self):

        msg = self.messages[0]

        self.processor.process(msg.payload)
        self.handler.assert_has_calls(msg)

    def test_backed_up_queue_is_cleared(self):

        # skip first message, so the rest will be waiting in queue
        for m in self.messages[1:]:
            self.processor.process(m.payload)

        # nothing was delivered yet
        self.handler.assert_not_called()

        # delivers the first message, so the queue will be processed
        self.processor.process(self.messages[0].payload)

        # all messages were delivered
        self.handler.assert_has_calls(call(m) for m in self.messages)