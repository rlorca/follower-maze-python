from fmaze.service import SimpleServer, PeerHandlerBuilder, EventHandlerBuilder
from fmaze.state import State
from fmaze.processor import MessageProcessor, Protocol

import asyncore

state = State()
processor = MessageProcessor(state)

with SimpleServer(Protocol.SERVER_EVENT_PORT, EventHandlerBuilder(processor)), \
    SimpleServer(Protocol.SERVER_PEER_PORT, PeerHandlerBuilder(state)):

    asyncore.loop()