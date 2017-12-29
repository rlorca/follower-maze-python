import asyncore
import logging


from io import StringIO
from fmaze.state import State

logger = logging.getLogger("service")
logger.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
#ch.setLevel(logging.ERROR)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(thread)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(ch)

state = State()

class BobServer(asyncore.dispatcher):

    def __init__(self, host, port, handler):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self.handler = handler

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        logger.info("Server closed {}", self.addr)


    def handle_accepted(self, sock, addr):
        self.handler(sock)


class EventHandler(asyncore.dispatcher):

    read_buffer_size = 8192

    def handle_read(self):
        data = self.recv(8192)
        logger.debug("Got message %s", len(data))
        if data:
            buffer = StringIO(data.decode("UTF-8"))
            for l in buffer.readlines():
                state.new_event(l)

class PeerHandler(asyncore.dispatcher_with_send):

    def handle_read(self):
        data = self.recv(256)
        if data:
            peer_id = data.decode("UTF-8").strip()
            logger.debug("Handling peer %s", peer_id)
            state.register_connection(peer_id, self)


with BobServer("0.0.0.0", 9090, EventHandler), \
     BobServer("0.0.0.0", 9099, PeerHandler):

    logger.info("Servers started")
    asyncore.loop()