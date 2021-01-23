from unittest import TestCase
from maxcube.message import Message

class TestMessage(TestCase):
    """ Test Max! Cube messages """

    def testDecodeValidMessage(self):
        line = b's:AARAAAAABrxTAWo=\r\n'
        msg = Message.decode(line)
        self.assertEquals(Message('s', 'AARAAAAABrxTAWo='), msg)
        self.assertEquals('S', msg.reply_cmd())
        self.assertEquals(line, msg.encode())

    def testDecodeEmptyMessage(self):
        self.assertEquals(Message(''), Message.decode(b'\r\n'))
