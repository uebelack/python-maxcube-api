import socket

from unittest import TestCase
from unittest.mock import MagicMock, call, patch
from maxcube.commander import Commander
from maxcube.connection import Connection
from maxcube.deadline import Deadline, Timeout
from maxcube.message import Message

TEST_TIMEOUT = Timeout('test', 1000.0)

@patch('socket.socket', spec=True)
class TestConnection(TestCase):
    """ Test Max! Cube connections """

    def connect(self, socketMock):
        self.socket = socketMock.return_value
        self.connection = Connection('host', 1234)
        self.socket.settimeout.assert_called_once_with(2.0)
        self.socket.connect.assert_called_once_with(('host', 1234))

    def testReadAMessage(self, socketMock):
        self.connect(socketMock)
        self.socket.recv.return_value = b'A:B\r\n'

        self.assertEqual(Message('A', 'B'),
            self.connection.recv(TEST_TIMEOUT.deadline()))
        self.socket.close.assert_not_called()

    def testReadPartialLine(self, socketMock):
        self.connect(socketMock)
        self.socket.recv.side_effect = [b'A:', b'B\r\n']

        self.assertEqual(Message('A', 'B'),
            self.connection.recv(TEST_TIMEOUT.deadline()))

    def testReadMultipleLines(self, socketMock):
        self.connect(socketMock)
        self.socket.recv.return_value = b'A:B\r\nC\r\n'

        self.assertEqual(Message('A', 'B'),
            self.connection.recv(TEST_TIMEOUT.deadline()))
        self.socket.recv.reset_mock()
        self.assertEqual(Message('C', ''),
            self.connection.recv(TEST_TIMEOUT.deadline()))

    def testReadAtConnectionClosing(self, socketMock):
        self.connect(socketMock)
        self.socket.recv.return_value = b''

        self.assertIsNone(self.connection.recv(TEST_TIMEOUT.deadline()))
        self.socket.close.assert_called_once()

    def testReadTimeout(self, socketMock):
        self.connect(socketMock)
        self.socket.recv.side_effect = [socket.timeout]

        self.assertIsNone(self.connection.recv(TEST_TIMEOUT.deadline()))
        self.socket.close.assert_not_called()

    def testSendMessage(self, socketMock):
        self.connect(socketMock)
        self.connection.send(Message('A', 'B'))
        self.socket.send.assert_called_with(b'A:B\r\n')

    def testCloseErrorsAreIgnored(self, socketMock):
        self.connect(socketMock)
        self.socket.close.side_effect = [OSError]
        self.connection.close()
        self.socket.close.assert_called_once()
