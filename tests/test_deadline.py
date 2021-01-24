from unittest import TestCase
from unittest.mock import MagicMock, call, patch
from maxcube.deadline import Deadline, Timeout

ZERO_TIMEOUT = Timeout('zero', 0)
ONE_TIMEOUT = Timeout('one', 1)
ROOT_TIMEOUT = Timeout('root', 10)

@patch('maxcube.deadline.time')
class TestDeadline(TestCase):
    """ Test Deadlines """

    def testDeadlineLowerBoundForRemainingTime(self, timeMock):
        timeMock.side_effect = [0, 0.4, 0.6]
        deadline = ONE_TIMEOUT.deadline()
        self.assertAlmostEqual(0.6, deadline.remaining(lower_bound=0.50))
        self.assertAlmostEqual(0.5, deadline.remaining(lower_bound=0.50))

    def testDeadlineUpperBoundForRemainingTime(self, timeMock):
        timeMock.side_effect = [0, 0.4, 0.6]
        deadline = ONE_TIMEOUT.deadline()
        self.assertAlmostEqual(0.5, deadline.remaining(upper_bound=0.50))
        self.assertAlmostEqual(0.4, deadline.remaining(upper_bound=0.50))

    def testDeadlineIsExpired(self, timeMock):
        timeMock.side_effect = [0, 0.4, 1.0, 1.000001]
        deadline = ONE_TIMEOUT.deadline()
        self.assertFalse(deadline.is_expired())
        self.assertTrue(deadline.is_expired())
        self.assertTrue(deadline.is_expired())

    def testZeroDeadlineIsAlreadyExpired(self, timeMock):
        timeMock.side_effect = [0.0, 0.0]
        deadline = ZERO_TIMEOUT.deadline()
        self.assertEquals('zero', deadline.fullname())
        self.assertTrue(deadline.is_expired())

    def testSubtimeoutHandling(self, timeMock):
        timeMock.side_effect = [0.0, 0.1, 0.2]
        deadline = ROOT_TIMEOUT.deadline()
        subdeadline = deadline.subtimeout(ONE_TIMEOUT)
        self.assertEquals('root:one', subdeadline.fullname())
        self.assertAlmostEqual(0.9, subdeadline.remaining())

    def testSubtimeoutHandlingWhenLargerThanTimeout(self, timeMock):
        timeMock.side_effect = [0.0, 9.1, 9.2]
        deadline = ROOT_TIMEOUT.deadline()
        subdeadline = deadline.subtimeout(ONE_TIMEOUT)
        self.assertAlmostEqual(0.8, subdeadline.remaining())

    def testToString(self, timeMock):
        timeMock.side_effect = [0.0, 0.1]
        deadline = ONE_TIMEOUT.deadline()
        self.assertEquals('Deadline one will expire in 0.900 seconds', str(deadline))

    def testToStringForExpiredDeadline(self, timeMock):
        timeMock.side_effect = [0.0, 1.1]
        deadline = ONE_TIMEOUT.deadline()
        self.assertEquals('Deadline one expired 0.100 seconds ago', str(deadline))
