import asyncore

from .logger import create_logger
from io import BytesIO
from .processor import Protocol

logger = create_logger(__name__)

class SimpleServer(asyncore.dispatcher):

    def __init__(self, port, handler_builder):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind(("0.0.0.0", port))
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

class HandlerBuilder:

    def __init__(self):
        self.builder = None

    def build(self, socket):
        self.builder(socket)


class EventHandlerBuilder(HandlerBuilder):

    def __init__(self, event_processor):

        class EventHandler(asyncore.dispatcher):

            def handle_read(self):
                data = self.recv(8192)
                if data:
                    for l in BytesIO(data).readlines():
                        event_processor.process_message(l)

        self.builder = EventHandler

class PeerHandlerBuilder(HandlerBuilder):

    def __init__(self, state):

        class PeerHandler(asyncore.dispatcher_with_send):

            def handle_read(self):
                data = self.recv(128)
                if data:
                    peer_id = data.decode(Protocol.ENCODING).strip()
                    logger.debug("New peer %s connected", peer_id)
                    state.register_connection(peer_id, self)

        self.builder = PeerHandler