import unittest
from maxcube.connection import MaxCubeConnection
from maxcube.cube import MaxCube
from maxcube.device import \
    MaxDevice, \
    MAX_CUBE, \
    MAX_THERMOSTAT, \
    MAX_THERMOSTAT_PLUS, \
    MAX_DEVICE_MODE_AUTOMATIC, \
    MAX_DEVICE_MODE_MANUAL

INIT_RESPONSE = \
    'H:KEQ0566338,0b6475,0113,00000000,74b7b6f7,00,32,0f0c19,1527,03,0000\n\r' \
    'M:00,01,VgIEAQdLaXRjaGVuBrxTAgZMaXZpbmcGvFoDCFNsZWVwaW5nCKuCBARXb3JrBrxcBAEGvFNLRVEwMzM2MTA4B0tpdGNoZW4BAQa8Wk' \
    'tFUTAzMzYxMDAGTGl2aW5nAgEIq4JLRVEwMzM1NjYyCFNsZWVwaW5nAwEGvFxLRVEwMzM2MTA0BFdvcmsEAQ==\r\n' \
    'C:0b6475,7QtkdQATAf9LRVEwNTY2MzM4AQsABEAAAAAAAAAAAP///////////////////////////wsABEAAAAAAAAAAQf////////////////' \
    '///////////2h0dHA6Ly93d3cubWF4LXBvcnRhbC5lbHYuZGU6ODAvY3ViZQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' \
    'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAENFVAAACgADAAAOEENFU1QAAwACAAAcIA==\r\n' \
    'C:06bc53,0ga8UwEBGP9LRVEwMzM2MTA4KCEyCQcYAzAM/wBESFUIRSBFIEUgRSBFIEUgRSBFIEUgRSBFIERIVQhFIEUgRSBFIEUgRSBFIEUgRS' \
    'BFIEUgREhUbETMVRRFIEUgRSBFIEUgRSBFIEUgRSBESFRsRMxVFEUgRSBFIEUgRSBFIEUgRSBFIERIVGxEzFUURSBFIEUgRSBFIEUgRSBFIEUgR' \
    'EhUbETMVRRFIEUgRSBFIEUgRSBFIEUgRSBESFRsRMxVFEUgRSBFIEUgRSBFIEUgRSBFIA==\r\n' \
    'C:06bc5a,0ga8WgECGP9LRVEwMzM2MTAwKCEyCQcYAzAM/wBESFUIRSBFIEUgRSBFIEUgRSBFIEUgRSBFIERIVQhFIEUgRSBFIEUgRSBFIEUgRS' \
    'BFIEUgREhUbETMVRRFIEUgRSBFIEUgRSBFIEUgRSBESFRsRMxVFEUgRSBFIEUgRSBFIEUgRSBFIERIVGxEzFUURSBFIEUgRSBFIEUgRSBFIEUgR' \
    'EhUbETMVRRFIEUgRSBFIEUgRSBFIEUgRSBESFRsRMxVFEUgRSBFIEUgRSBFIEUgRSBFIA==\r\n' \
    'C:06bc5c,0ga8XAEEGP9LRVEwMzM2MTA0KCEyCQcYAzAM/wBESFUIRSBFIEUgRSBFIEUgRSBFIEUgRSBFIERIVQhFIEUgRSBFIEUgRSBFIEUgR' \
    'SBFIEUgREhUbETMVRRFIEUgRSBFIEUgRSBFIEUgRSBESFRsRMxVFEUgRSBFIEUgRSBFIEUgRSBFIERIVGxEzFUURSBFIEUgRSBFIEUgRSBFIEU' \
    'gREhUbETMVRRFIEUgRSBFIEUgRSBFIEUgRSBESFRsRMxVFEUgRSBFIEUgRSBFIEUgRSBFIA==\r\n' \
    'C:08ab82,0girggEDGP9LRVEwMzM1NjYyKCEyCQcYAzAM/wBEYFRsRMxFFEUgRSBFIEUgRSBFIEUgRSBFIERgVGxEzEUURSBFIEUgRSBFIEUgR' \
    'SBFIEUgRGBUbETMRRRFIEUgRSBFIEUgRSBFIEUgRSBEYFRsRMxFFEUgRSBFIEUgRSBFIEUgRSBFIERgVGxEzEUURSBFIEUgRSBFIEUgRSBFIEU' \
    'gRGBUbETMRRRFIEUgRSBFIEUgRSBFIEUgRSBEYFRsRMxFFEUgRSBFIEUgRSBFIEUgRSBFIA==\r\n' \
    'L:Cwa8U/EaGBsqAOwACwa8WgkSGCMqAOcACwa8XAkSGAsqAOcACwirggMaGAAiAAAA'


class MaxCubeConnectionMock(MaxCubeConnection):
    def __init__(self):
        super().__init__(None, None)
        self.command = None

    def connect(self):
        self.response = INIT_RESPONSE
        return

    def send(self, command):
        self.command = command

    def disconnect(self):
        return


class TestMaxCube(unittest.TestCase):
    """ Test the Max! Cube. """

    def setUp(self):
        self.cube = MaxCube(MaxCubeConnectionMock())

    def test_init(self):
        self.assertEqual('0b6475', self.cube.rf_address)
        self.assertEqual('Cube', self.cube.name)
        self.assertEqual('01.13', self.cube.firmware_version)
        self.assertEqual(4, len(self.cube.devices))

    def test_parse_response(self):
        self.cube.parse_response(INIT_RESPONSE)
        self.assertEqual('0b6475', self.cube.rf_address)
        self.assertEqual('Cube', self.cube.name)
        self.assertEqual('01.13', self.cube.firmware_version)
        self.assertEqual(4, len(self.cube.devices))

    def test_parse_c_message(self):
        self.cube.parse_c_message('C:0b6475,7QtkdQATAf9LRVEwNTY2MzM4AAsABEAAAAAAAAAAAP///////////////////////////'
                                  'wsABEAAAAAAAAAAQf///////////////////////////2h0dHA6Ly93d3cubWF4LXBvcnRhbC5lbHY'
                                  'uZGU6ODAvY3ViZQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                                  'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAENFVAAACgADAAAOEEN'
                                  'FU1QAAwACAAAcIA==')
        device = self.cube.devices[0]
        self.assertEqual(4.5, device.min_temperature)
        self.assertEqual(25.0, device.max_temperature)

    def test_parse_h_message(self):
        self.cube.parse_h_message('H:KEQ0566338,0b6444,0113,00000000,335b04d2,33,32,0f0c1d,101c,03,0000')
        self.assertEqual('0b6444', self.cube.rf_address)
        self.assertEqual('01.13', self.cube.firmware_version)

    def test_parse_m_message(self):
        self.cube.parse_m_message('M:00,01,VgIEAQdLaXRjaGVuBrxTAgZMaXZpbmcGvFoDCFNsZWVwaW5nCKuCBARXb3JrBrxcBAEGvF'
                                  'NLRVEwMzM2MTA4B0tpdGNoZW4BAQa8WktFUTAzMzYxMDAGTGl2aW5nAgEIq4JLRVEwMzM1NjYyCFNs'
                                  'ZWVwaW5nAwEGvFxLRVEwMzM2MTA0BFdvcmsEAQ==')
        self.assertEqual('6BC53', self.cube.devices[0].rf_address)
        self.assertEqual('Kitchen', self.cube.devices[0].name)
        self.assertEqual('6BC5A', self.cube.devices[1].rf_address)
        self.assertEqual('Living', self.cube.devices[1].name)
        self.assertEqual('8AB82', self.cube.devices[2].rf_address)
        self.assertEqual('Sleeping', self.cube.devices[2].name)
        self.assertEqual('6BC5C', self.cube.devices[3].rf_address)
        self.assertEqual('Work', self.cube.devices[3].name)

    def test_parse_l_message(self):
        self.cube.parse_l_message('L:Cwa8U/ESGAAiAAAACwa8WgkSGAAiAAAACwa8XAkSGAUiAAAACwirggMSGAUiAAAA')
        device = self.cube.devices[0]
        self.assertEqual(MAX_DEVICE_MODE_AUTOMATIC, device.mode)
        self.assertEqual(23.6, device.actual_temperature)
        self.assertEqual(17.0, device.target_temperature)
        self.cube.parse_l_message('L:Cwa8U/ESGQkhALMACwa8WgkSGQAhAMAACwa8XAkSGQUhALIACwirggMSGQUhAAAA')
        device = self.cube.devices[0]
        self.assertEqual(MAX_DEVICE_MODE_MANUAL, device.mode)
        self.assertEqual(17.9, device.actual_temperature)
        self.assertEqual(16.5, device.target_temperature)

    def test_resolve_device_mode(self):
        self.assertEqual(MAX_DEVICE_MODE_AUTOMATIC, self.cube.resolve_device_mode(24))
        self.assertEqual(MAX_DEVICE_MODE_MANUAL, self.cube.resolve_device_mode(25))

    def test_is_thermostat(self):
        device = MaxDevice()
        device.type = MAX_CUBE
        self.assertEqual(False, self.cube.is_thermostat(device))
        device.type = MAX_THERMOSTAT
        self.assertEqual(True, self.cube.is_thermostat(device))
        device.type = MAX_THERMOSTAT_PLUS
        self.assertEqual(True, self.cube.is_thermostat(device))

    def test_set_target_temperature(self):
        self.cube.set_target_temperature(self.cube.devices[0], 24.5)
        self.assertEqual('s:AARAAAAABrxTATE=\r\n', self.cube.connection.command)
        self.assertEqual(24.5, self.cube.devices[0].target_temperature)
        self.cube.set_target_temperature(self.cube.devices[0], 24.6)
        self.assertEqual(24.5, self.cube.devices[0].target_temperature)



