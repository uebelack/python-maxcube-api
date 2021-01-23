import base64

from unittest import TestCase
from unittest.mock import MagicMock, call, patch
from maxcube.commander import Commander
from maxcube.connection import Connection
from maxcube.deadline import Deadline, Timeout
from maxcube.message import Message

L_CMD = Message('l')
L_CMD_SUCCESS = Message('L')
S_CMD_HEX = 'FF00'
S_CMD = Message('s', base64.b64encode(bytearray.fromhex(S_CMD_HEX)).decode('utf-8'))
S_CMD_SUCCESS = Message('S', '00,0,31')
S_CMD_ERROR = Message('S', '100,1,31')
S_CMD_THROTTLE_ERROR = Message('S', '100,1,0')

TEST_TIMEOUT = Timeout('test', 1.0)

@patch('maxcube.commander.Connection', spec=True)
class TestCommander(TestCase):
    """ Test Max! Cube command handler """

    def init(self, ClassMock):
        self.connection = ClassMock.return_value
        self.commander = Commander('host', 1234)

    def testDisconnectIsNoopIfAlreadyDisconnected(self, ClassMock):
        self.init(ClassMock)
        self.commander.disconnect()

        ClassMock.assert_not_called()

        self.connection.send.assert_not_called()
        self.connection.recv.assert_not_called()
        self.connection.close.assert_not_called()

    def testUpdateOpensNewConnectionIfDisconnected(self, ClassMock):
        messages = [Message('H'), Message('L')]
        self.init(ClassMock)
        self.connection.recv.side_effect = messages

        self.assertEqual(messages, self.commander.update())

        self.connection.send.assert_not_called()
        self.assertEqual(2, self.connection.recv.call_count)
        self.connection.close.assert_not_called()

    def testUpdateSendsCommandAfterAfterTimeout(self, ClassMock):
        messages = [Message('H'), None]
        self.init(ClassMock)
        self.connection.recv.side_effect = messages

        self.assertEqual(messages[:1], self.commander.update())

        self.connection.send.assert_not_called()
        self.assertEqual(2, self.connection.recv.call_count)
        self.connection.close.assert_not_called()

        self.connection.recv.reset_mock()
        self.__mockCommandResponse(L_CMD_SUCCESS)

        self.assertEqual([L_CMD_SUCCESS], self.commander.update())

        self.connection.send.assert_called_once_with(Message('l'))
        self.assertEqual(2, self.connection.recv.call_count)
        self.connection.close.assert_not_called()

    def testSendRadioMsgAutoconnects(self, ClassMock = None):
        self.init(ClassMock)
        self.connection.recv.side_effect = [
            L_CMD_SUCCESS, # connection preambule
            S_CMD_SUCCESS
        ]

        self.assertTrue(self.commander.send_radio_msg(S_CMD_HEX))
        self.connection.send.assert_called_once_with(S_CMD)
        self.assertEqual(2, self.connection.recv.call_count)
        self.connection.close.assert_not_called()

    def testSendRadioMsgReusesConnection(self, ClassMock):
        self.testSendRadioMsgAutoconnects()

        self.connection.send.reset_mock()
        self.connection.recv.reset_mock()
        self.connection.recv.side_effect = [
            None,
            S_CMD_SUCCESS
        ]

        self.assertTrue(self.commander.send_radio_msg(S_CMD_HEX))

        self.connection.send.assert_called_once_with(S_CMD)
        self.assertEqual(2, self.connection.recv.call_count)
        self.connection.close.assert_not_called()

    def testSendRadioMsgClosesConnectionOnErrorAndRetriesIfReusingConnection(self, ClassMock):
        self.testSendRadioMsgAutoconnects()

        self.connection.recv.reset_mock()
        self.connection.recv.side_effect = [
            None, # First read before first try
        ]
        self.connection.send.reset_mock()
        self.connection.send.side_effect = [ OSError ]

        newConnection = MagicMock(Connection)
        ClassMock.side_effect = [newConnection]
        newConnection.recv.side_effect = [
            L_CMD_SUCCESS, # Connection preamble
            S_CMD_SUCCESS,
        ]

        self.assertTrue(self.commander.send_radio_msg(S_CMD_HEX))

        self.connection.recv.assert_called_once()
        self.connection.send.assert_called_once_with(S_CMD)
        self.connection.close.assert_called_once()

        self.assertEqual(2, newConnection.recv.call_count)
        newConnection.send.assert_called_once_with(S_CMD)
        newConnection.close.assert_not_called()

    def __send_radio_msg(self, msg: Message, deadline: Deadline):
        with patch('maxcube.commander.Timeout.deadline') as deadlineMock:
            deadlineMock.return_value = deadline
            return self.commander.send_radio_msg(msg)

    def testSendRadioMsgShouldNotRetryOnErrorWhenConnectionIsNew(self, ClassMock):
        self.init(ClassMock)
        self.connection.recv.side_effect = [ L_CMD_SUCCESS ]
        self.connection.send.side_effect = [ OSError ]

        deadline = MagicMock(Deadline)
        deadline.is_expired.side_effect = [False, True]
        deadline.subtimeout.return_value = TEST_TIMEOUT.deadline()

        self.assertFalse(self.__send_radio_msg(S_CMD_HEX, deadline))

        self.connection.send.assert_called_once_with(S_CMD)
        self.connection.recv.assert_called_once()
        self.connection.close.assert_called_once()

    def testSendRadioMsgFailsOnLogicalError(self, ClassMock):
        self.init(ClassMock)
        self.connection.recv.side_effect = [ L_CMD_SUCCESS, S_CMD_ERROR ]

        deadline: Deadline = MagicMock(Deadline)
        deadline.is_expired.side_effect = [False, True]
        deadline.subtimeout.return_value = TEST_TIMEOUT.deadline()
        self.assertFalse(self.__send_radio_msg(S_CMD_HEX, deadline))

        self.connection.send.assert_called_once_with(S_CMD)
        self.assertEqual(2, self.connection.recv.call_count)
        self.connection.close.assert_not_called()
        deadline.remaining.assert_not_called()

    def testSendRadioMsgRetriesOnThrottlingError(self, ClassMock):
        self.init(ClassMock)
        self.connection.recv.side_effect = [ L_CMD_SUCCESS, S_CMD_THROTTLE_ERROR ]

        deadline: Deadline = MagicMock(Deadline)
        deadline.is_expired.side_effect = [False, True]
        deadline.remaining.return_value = 0.1
        deadline.subtimeout.return_value = TEST_TIMEOUT.deadline()
        self.assertFalse(self.__send_radio_msg(S_CMD_HEX, deadline))

        self.connection.send.assert_called_once_with(S_CMD)
        self.assertEqual(2, self.connection.recv.call_count)
        self.connection.close.assert_not_called()
        deadline.remaining.assert_called_once()

    def __mockCommandResponse(self, response):
        self.connection.recv.side_effect = [None, response]
