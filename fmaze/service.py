import asyncore

from fmaze.state import State
from .logger import create_logger
from .processor import Protocol, MessageProcessor

from io import BytesIO
from typing import Callable


logger = create_logger(__name__)


class HandlerBuilder:

    def __init__(self):
        self.builde : Callable = None

    def build(self, socket):
        self.builder(socket)


class EventHandlerBuilder(HandlerBuilder):

    def __init__(self, event_processor: MessageProcessor):

        class EventHandler(asyncore.dispatcher):

            def handle_read(self):
                data = self.recv(8_192)
                if data:
                    for l in BytesIO(data).readlines():
                        event_processor.process_message(l)

        self.builder = EventHandler


class PeerHandlerBuilder(HandlerBuilder):

    def __init__(self, state: State):

        class PeerHandler(asyncore.dispatcher_with_send):

            def handle_read(self):
                data = self.recv(128)
                if data:
                    peer_id = data.decode(Protocol.ENCODING).strip()
                    logger.debug("New peer %s connected", peer_id)
                    state.register_connection(peer_id, self)

        self.builder = PeerHandler


class SimpleServer(asyncore.dispatcher):

    def __init__(self, address, port, handler_builder : HandlerBuilder):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind((address, port))
        self.listen(5)
        self.handler_builder = handler_builder
        self.port = port

    def __enter__(self):
        logger.info("Service %d started.", self.port)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        logger.info("Service %d closed.", self.port)

    def handle_accepted(self, sock, addr):
        self.handler_builder.build(sock)