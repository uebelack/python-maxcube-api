from unittest import TestCase
from unittest.mock import patch

from maxcube.deadline import Deadline, Timeout

ZERO_TIMEOUT = Timeout("zero", 0)
ONE_TIMEOUT = Timeout("one", 1)
ROOT_TIMEOUT = Timeout("root", 10)


@patch("maxcube.deadline.time")
class TestDeadline(TestCase):
    """ Test Deadlines """

    def testDeadlineLowerBoundForRemainingTime(self, timeMock):
        timeMock.side_effect = [0, 0.4, 0.6]
        deadline = Deadline(ONE_TIMEOUT)
        self.assertAlmostEqual(0.6, deadline.remaining(lower_bound=0.50))
        self.assertAlmostEqual(0.5, deadline.remaining(lower_bound=0.50))

    def testDeadlineUpperBoundForRemainingTime(self, timeMock):
        timeMock.side_effect = [0, 0.4, 0.6]
        deadline = Deadline(ONE_TIMEOUT)
        self.assertAlmostEqual(0.5, deadline.remaining(upper_bound=0.50))
        self.assertAlmostEqual(0.4, deadline.remaining(upper_bound=0.50))

    def testDeadlineIsExpired(self, timeMock):
        timeMock.side_effect = [0, 0.4, 1.0, 1.000001]
        deadline = Deadline(ONE_TIMEOUT)
        self.assertFalse(deadline.is_expired())
        self.assertTrue(deadline.is_expired())
        self.assertTrue(deadline.is_expired())

    def testZeroDeadlineIsAlreadyExpired(self, timeMock):
        timeMock.return_value = 0.0
        deadline = Deadline(ZERO_TIMEOUT)
        self.assertEqual("zero[0/0]", deadline.fullname())
        self.assertTrue(deadline.is_expired())

    def testSubtimeoutHandling(self, timeMock):
        timeMock.side_effect = [0.0, 0.1, 0.2, 0.2, 0.3]
        deadline = Deadline(ROOT_TIMEOUT)
        subdeadline = deadline.subtimeout(ONE_TIMEOUT)
        self.assertEqual("root[9.8/10]:one[0.9/1]", subdeadline.fullname())
        self.assertAlmostEqual(0.8, subdeadline.remaining())

    def testSubtimeoutHandlingWhenLargerThanTimeout(self, timeMock):
        timeMock.side_effect = [0.0, 9.1, 9.2]
        deadline = Deadline(ROOT_TIMEOUT)
        subdeadline = deadline.subtimeout(ONE_TIMEOUT)
        self.assertAlmostEqual(0.8, subdeadline.remaining())

    def testToString(self, timeMock):
        timeMock.side_effect = [0.0, 0.1]
        deadline = Deadline(ONE_TIMEOUT)
        self.assertEqual("Deadline one[0.9/1]", str(deadline))

    def testToStringForExpiredDeadline(self, timeMock):
        timeMock.side_effect = [0.0, 1.1]
        deadline = Deadline(ONE_TIMEOUT)
        self.assertEqual("Deadline one[0/1]", str(deadline))
