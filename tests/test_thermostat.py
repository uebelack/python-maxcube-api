from unittest import TestCase

from maxcube.thermostat import MaxThermostat


class TestMessage(TestCase):
    """ Test Max! thermostat """

    def testGetCurrentTemperatureReturnsNoneIfUninitialized(self):
        t = MaxThermostat()
        self.assertIsNone(t.get_current_temp_in_auto_mode())
