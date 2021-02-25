from unittest import TestCase
from maxcube.message import Message

class TestMessage(TestCase):
    """ Test Max! Cube messages """

    def testDecodeValidMessage(self):
        line = b's:AARAAAAABrxTAWo=\r\n'
        msg = Message.decode(line)
        self.assertEqual(Message('s', 'AARAAAAABrxTAWo='), msg)
        self.assertEqual('S', msg.reply_cmd())
        self.assertEqual(line, msg.encode())

    def testDecodeEmptyMessage(self):
        self.assertEqual(Message(''), Message.decode(b'\r\n'))
