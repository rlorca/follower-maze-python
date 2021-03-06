from fmaze.service import SimpleServer, PeerHandlerBuilder, EventHandlerBuilder
from fmaze.state import State
from fmaze.processor import MessageProcessor, Protocol

import asyncore

import fmaze.logger

logger = fmaze.logger.create_logger(__name__)

logger.info("Starting application")

ip = "0.0.0.0"

with State() as state, \
     SimpleServer(ip, Protocol.SERVER_EVENT_PORT, EventHandlerBuilder(MessageProcessor(state))), \
     SimpleServer(ip, Protocol.SERVER_PEER_PORT, PeerHandlerBuilder(state)):

    try:
        asyncore.loop()
    except KeyboardInterrupt as e:
        logger.info("Stop requested")


logger.info("Application terminated")