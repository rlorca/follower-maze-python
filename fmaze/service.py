import asyncore
import logging

from io import BytesIO
from fmaze.state import State
from fmaze.processor import MessageProcessor, Protocol

def initialize_logger():
    logger = logging.getLogger("service")
    logger.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(thread)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)

    return logger

class SimpleServer(asyncore.dispatcher):

    def __init__(self, port, handler):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind(("0.0.0.0", port))
        self.listen(5)
        self.handler = handler
        self.port = port

    def __enter__(self):
        logger.info("Service %d started.", self.port)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        logger.info("Service %d closed.", self.port)

    def handle_accepted(self, sock, addr):
        self.handler(sock)


class EventHandler(asyncore.dispatcher):

    def handle_read(self):
        data = self.recv(8192)
        if data:
            for l in BytesIO(data).readlines():
                processor.process(l)


class PeerHandler(asyncore.dispatcher_with_send):

    def handle_read(self):
        data = self.recv(256)
        if data:
            peer_id = data.decode(Protocol.ENCODING).strip()
            logger.debug("Handling peer %s", peer_id)
            state.register_connection(peer_id, self)


logger = initialize_logger()

state = State()
processor = MessageProcessor(state)

with SimpleServer(Protocol.SERVER_EVENT_PORT, EventHandler), \
     SimpleServer(Protocol.SERVER_PEER_PORT, PeerHandler):

    logger.info("Starting service loop")
    asyncore.loop()