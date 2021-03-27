import logging
import socket

from .deadline import Deadline
from .message import Message

logger = logging.getLogger(__name__)

BLOCK_SIZE = 4096
DEFAULT_TIMEOUT = 2.0


class Connection(object):
    def __init__(self, host: str, port: int):
        self.__buffer: bytearray = bytearray()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.settimeout(DEFAULT_TIMEOUT)
        self.__socket.connect((host, port))
        logger.debug("Connected to %s:%d!" % (host, port))

    def __read_buffered_msg(self) -> Message:
        buf = self.__buffer
        pos = buf.find(b"\r\n")
        if pos < 0:
            return None
        result = buf[0:pos]
        del buf[0 : pos + 2]
        return Message.decode(result)

    def recv(self, deadline: Deadline) -> Message:
        msg = self.__read_buffered_msg()
        try:
            while msg is None:
                self.__socket.settimeout(deadline.remaining(lower_bound=0.001))
                tmp = self.__socket.recv(BLOCK_SIZE)
                if len(tmp) > 0:
                    self.__buffer.extend(tmp)
                    msg = self.__read_buffered_msg()
                    logger.debug("received: %s" % msg)
                else:
                    logger.debug("Connection shutdown by remote peer")
                    self.close()
                    return None
        except socket.timeout:
            logger.debug("readline timed out")
        finally:
            self.__socket.settimeout(DEFAULT_TIMEOUT)
        return msg

    def send(self, msg: Message):
        self.__socket.send(msg.encode())
        logger.debug("sent: %s" % msg)

    def close(self):
        try:
            self.__socket.close()
            logger.debug("closed")
        except Exception:
            logger.debug("Unable to close connection. Dropping it...")
