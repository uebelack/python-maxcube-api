import socket
import logging

logger = logging.getLogger(__name__)


class MaxCubeConnection(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.response = None

    def connect(self):
        logger.debug('Connecting to Max! Cube at ' + self.host + ':' + str(self.port))
        try:
            if self.socket:
                self.disconnect()
        except:
            logger.debug('Tried disconnecting from cube, caught Exception probably due to stale connection.')

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(2)
        self.socket.connect((self.host, self.port))
        self.read()

    def read(self):
        buffer_size = 4096
        buffer = bytearray([])
        more = True

        while more:
            try:
                tmp = self.socket.recv(buffer_size)
                more = len(tmp) > 0
                buffer += tmp
            except socket.timeout:
                break
        self.response = buffer.decode('utf-8')

    def send(self, command):
        self.socket.send(command.encode('utf-8'))
        self.read()

    def disconnect(self):
        if self.socket:
            self.send('q:\r\n')
            self.socket.close()
        self.socket = None
