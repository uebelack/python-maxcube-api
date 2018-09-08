import unittest
from maxcube.connection import MaxCubeConnection
from maxcube.cube import MaxCube
from maxcube.device import \
    MaxDevice, \
    MAX_CUBE, \
    MAX_THERMOSTAT, \
    MAX_THERMOSTAT_PLUS, \
    MAX_WALL_THERMOSTAT, \
    MAX_WINDOW_SHUTTER, \
    MAX_DEVICE_MODE_AUTOMATIC, \
    MAX_DEVICE_MODE_MANUAL, \
    MAX_DEVICE_MODE_BOOST
from maxcube.room import MaxRoom

INIT_RESPONSE_1 = \
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

INIT_RESPONSE_2 = \
    'H:JEQ0341267,015d2a,0113,00000000,0336f10a,4b,29,110203,172a,03,0000\n\r' \
    'M:00,01,VgICAQpCYWRlemltbWVyDi66AgpXb2huemltbWVyAAAAAwEOLrpLRVExMDg2NDM3ClRoZXJtb3N0YXQBAwoIgUtFUTA2NTU3NDMOV2' \
    'FuZHRoZXJtb3N0YXQCBAyisktFUTA4Mzk3NzgORmVuc3RlcmtvbnRha3QBAQ==\n\r' \
    'C:015d2a,7QFdKgATAf9KRVEwMzQxMjY3AQsABEAAAAAAAAAAAP///////////////////////////wsABEAAAAAAAAAAQf///////////////' \
    '////////////2h0dHA6Ly9tYXguZXEtMy5kZTo4MC9jdWJlADAvbG9va3VwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' \
    'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAENFVAAACgADAAAOEENFU1QAAwACAAAcIA==' \
    '\n\r' \
    'C:0a0881,zgoIgQMCEP9LRVEwNjU1NzQzKyE9CURIVQhFIEUgRSBFIEUgRSBFIEUgRSBFIEUgREhVCEUgRSBFIEUgRSBFIEUgRSBFIEUgRSBES' \
    'FRsRMxVFEUgRSBFIEUgRSBFIEUgRSBFIERIVGxEzFUURSBFIEUgRSBFIEUgRSBFIEUgREhUbETMVRRFIEUgRSBFIEUgRSBFIEUgRSBESFRsRMx' \
    'VFEUgRSBFIEUgRSBFIEUgRSBFIERIVGxEzFUURSBFIEUgRSBFIEUgRSBFIEUgBxgw\n\r' \
    'C:0ca2b2,EQyisgQBFA9LRVEwODM5Nzc4\n\r' \
    'C:0e2eba,0g4uugEBEKBLRVExMDg2NDM3KyE9CQcYAzAM/wAgYFR4ISAhICEgISAhIEUgRSBFIEUgRSBFICBgVHghICEgISAhICEgRSBFIEUgR' \
    'SBFIEUgIEJUTiEfISAhICEgISBFIEUgRSBFIEUgRSAgQlROIR8hICEgISAhIEUgRSBFIEUgRSBFICBCVE4hHyEgISAhICEgRSBFIEUgRSBFIEU' \
    'gIEJUTiEfISAhICEgISBFIEUgRSBFIEUgRSAgQlROIR8hICEgISAhIEUgRSBFIEUgRSBFIA==\n\r' \
    'L:DAoIgewSGAQQAAAA5QYMorL3EhALDi66ChIYABAAAAA=\n\r' 

class MaxCubeConnectionMock(MaxCubeConnection):
    def __init__(self, init_response):
        super(MaxCubeConnectionMock, self).__init__(None, None)
        self.command = None
        self.init_response = init_response

    def connect(self):
        self.response = self.init_response
        return

    def send(self, command):
        self.command = command

    def disconnect(self):
        return


class TestMaxCube(unittest.TestCase):
    """ Test the Max! Cube. """

    def setUp(self):
        self.cube = MaxCube(MaxCubeConnectionMock(INIT_RESPONSE_1))

    def test_init(self):
        self.assertEqual('0b6475', self.cube.rf_address)
        self.assertEqual('Cube', self.cube.name)
        self.assertEqual('01.13', self.cube.firmware_version)
        self.assertEqual(4, len(self.cube.devices))

    def test_parse_response(self):
        self.cube.parse_response(INIT_RESPONSE_1)
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
        self.assertEqual('06BC53', self.cube.devices[0].rf_address)
        self.assertEqual('Kitchen', self.cube.devices[0].name)
        self.assertEqual('06BC5A', self.cube.devices[1].rf_address)
        self.assertEqual('Living', self.cube.devices[1].name)
        self.assertEqual('08AB82', self.cube.devices[2].rf_address)
        self.assertEqual('Sleeping', self.cube.devices[2].name)
        self.assertEqual('06BC5C', self.cube.devices[3].rf_address)
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
        self.assertEqual(False, device.is_thermostat())
        device.type = MAX_THERMOSTAT
        self.assertEqual(True, device.is_thermostat())
        device.type = MAX_THERMOSTAT_PLUS
        self.assertEqual(True, device.is_thermostat())

    def test_set_target_temperature(self):
        self.cube.set_target_temperature(self.cube.devices[0], 24.5)
        self.assertEqual('s:AARAAAAABrxTATE=\r\n', self.cube.connection.command)
        self.assertEqual(24.5, self.cube.devices[0].target_temperature)
        self.cube.set_target_temperature(self.cube.devices[0], 24.6)
        self.assertEqual(24.5, self.cube.devices[0].target_temperature)


class TestMaxCubeExtended(unittest.TestCase):
    """ Test the Max! Cube. """

    def setUp(self):
        self.cube = MaxCube(MaxCubeConnectionMock(INIT_RESPONSE_2))

    def test_init(self):
        self.assertEqual('015d2a', self.cube.rf_address)
        self.assertEqual('Cube', self.cube.name)
        self.assertEqual('01.13', self.cube.firmware_version)
        self.assertEqual(3, len(self.cube.devices))

    def test_parse_response(self):
        self.cube.parse_response(INIT_RESPONSE_2)
        self.assertEqual('015d2a', self.cube.rf_address)
        self.assertEqual('Cube', self.cube.name)
        self.assertEqual('01.13', self.cube.firmware_version)
        self.assertEqual(3, len(self.cube.devices))

    def test_parse_c_message_thermostat(self):
        device = self.cube.devices[0]
        self.assertEqual(21.5, device.comfort_temperature)
        self.assertEqual(16.5, device.eco_temperature)
        self.assertEqual(4.5, device.min_temperature)
        self.assertEqual(30.5, device.max_temperature)
        device = self.cube.devices[1]
        self.assertEqual(21.5, device.comfort_temperature)
        self.assertEqual(16.5, device.eco_temperature)
        self.assertEqual(4.5, device.min_temperature)
        self.assertEqual(30.5, device.max_temperature)
        device = self.cube.devices[2]
        self.assertEqual(1, device.initialized)

    def test_parse_h_message(self):
        self.cube.parse_h_message('H:KEQ0566338,0b6444,0113,00000000,335b04d2,33,32,0f0c1d,101c,03,0000')
        self.assertEqual('0b6444', self.cube.rf_address)
        self.assertEqual('01.13', self.cube.firmware_version)

    def test_parse_m_message(self):
        self.cube.parse_m_message('M:00,01,VgIEAQdLaXRjaGVuBrxTAgZMaXZpbmcGvFoDCFNsZWVwaW5nCKuCBARXb3JrBrxcBAEGvF'
                                  'NLRVEwMzM2MTA4B0tpdGNoZW4BAQa8WktFUTAzMzYxMDAGTGl2aW5nAgEIq4JLRVEwMzM1NjYyCFNs'
                                  'ZWVwaW5nAwEGvFxLRVEwMzM2MTA0BFdvcmsEAQ==')
        self.assertEqual('0E2EBA', self.cube.devices[0].rf_address)
        self.assertEqual('Thermostat', self.cube.devices[0].name)
        self.assertEqual(MAX_THERMOSTAT, self.cube.devices[0].type)
        self.assertEqual('KEQ1086437', self.cube.devices[0].serial)
        self.assertEqual(1, self.cube.devices[0].room_id)

        self.assertEqual('0A0881', self.cube.devices[1].rf_address)
        self.assertEqual('Wandthermostat', self.cube.devices[1].name)
        self.assertEqual(MAX_WALL_THERMOSTAT, self.cube.devices[1].type)
        self.assertEqual('KEQ0655743', self.cube.devices[1].serial)
        self.assertEqual(2, self.cube.devices[1].room_id)

        self.assertEqual('0CA2B2', self.cube.devices[2].rf_address)
        self.assertEqual('Fensterkontakt', self.cube.devices[2].name)
        self.assertEqual(MAX_WINDOW_SHUTTER, self.cube.devices[2].type)
        self.assertEqual('KEQ0839778', self.cube.devices[2].serial)
        self.assertEqual(1, self.cube.devices[3].room_id)

        self.assertEqual('Badezimmer', self.cube.rooms[0].name)
        self.assertEqual(1, self.cube.rooms[0].id)

        self.assertEqual('Wohnzimmer', self.cube.rooms[1].name)
        self.assertEqual(2, self.cube.rooms[1].id)

    def test_parse_l_message(self):
        device = self.cube.devices[0]
        self.assertEqual(MAX_DEVICE_MODE_AUTOMATIC, device.mode)
        self.assertEqual(None, device.actual_temperature)
        self.assertEqual(8.0, device.target_temperature)

        device = self.cube.devices[1]
        self.assertEqual(MAX_DEVICE_MODE_AUTOMATIC, device.mode)
        self.assertEqual(22.9, device.actual_temperature)
        self.assertEqual(8.0, device.target_temperature)
        
        device = self.cube.devices[2]
        self.assertEqual(False, device.is_open)

    def test_resolve_device_mode(self):
        self.assertEqual(MAX_DEVICE_MODE_AUTOMATIC, self.cube.resolve_device_mode(24))
        self.assertEqual(MAX_DEVICE_MODE_MANUAL, self.cube.resolve_device_mode(25))

    def test_is_thermostat(self):
        device = MaxDevice()
        device.type = MAX_CUBE
        self.assertEqual(False, device.is_thermostat())
        device.type = MAX_THERMOSTAT
        self.assertEqual(True, device.is_thermostat())
        device.type = MAX_THERMOSTAT_PLUS
        self.assertEqual(True, device.is_thermostat())
        device.type = MAX_WALL_THERMOSTAT
        self.assertEqual(False, device.is_thermostat())
        device.type = MAX_WINDOW_SHUTTER
        self.assertEqual(False, device.is_thermostat())

    def test_is_wall_thermostat(self):
        device = MaxDevice()
        device.type = MAX_CUBE
        self.assertEqual(False, device.is_wallthermostat())
        device.type = MAX_THERMOSTAT
        self.assertEqual(False, device.is_wallthermostat())
        device.type = MAX_THERMOSTAT_PLUS
        self.assertEqual(False, device.is_wallthermostat())
        device.type = MAX_WALL_THERMOSTAT
        self.assertEqual(True, device.is_wallthermostat())
        device.type = MAX_WINDOW_SHUTTER
        self.assertEqual(False, device.is_wallthermostat())

    def test_is_window_shutter(self):
        device = MaxDevice()
        device.type = MAX_CUBE
        self.assertEqual(False, device.is_windowshutter())
        device.type = MAX_THERMOSTAT
        self.assertEqual(False, device.is_windowshutter())
        device.type = MAX_THERMOSTAT_PLUS
        self.assertEqual(False, device.is_windowshutter())
        device.type = MAX_WALL_THERMOSTAT
        self.assertEqual(False, device.is_windowshutter())
        device.type = MAX_WINDOW_SHUTTER
        self.assertEqual(True, device.is_windowshutter())

    def test_set_target_temperature_thermostat(self):
        self.cube.set_target_temperature(self.cube.devices[0], 24.5)
        self.assertEqual('s:AARAAAAADi66ATE=\r\n', self.cube.connection.command)
        self.assertEqual(24.5, self.cube.devices[0].target_temperature)

    def test_set_target_temperature_windowshutter(self):
        self.cube.set_target_temperature(self.cube.devices[2], 24.5)
        self.assertEqual(None, self.cube.connection.command)

    def test_set_mode_thermostat(self):
        self.cube.set_mode(self.cube.devices[0], MAX_DEVICE_MODE_MANUAL)
        self.assertEqual('s:AARAAAAADi66AVA=\r\n', self.cube.connection.command)
        self.assertEqual(MAX_DEVICE_MODE_MANUAL, self.cube.devices[0].mode)

    def test_set_mode_windowshutter(self):
        self.cube.set_mode(self.cube.devices[2], 24.5)
        self.assertEqual(None, self.cube.connection.command)

    def test_set_temperature_mode_thermostat(self):
        self.cube.set_temperature_mode(self.cube.devices[2], 24.5, MAX_DEVICE_MODE_BOOST)
        self.assertEqual(None, self.cube.connection.command)

    def test_get_devices(self):
        devices = self.cube.get_devices()
        self.assertEqual(3, len(devices))

    def test_device_by_rf(self):
        device = self.cube.device_by_rf('0CA2B2')

        self.assertEqual('0CA2B2', device.rf_address)
        self.assertEqual('Fensterkontakt', device.name)
        self.assertEqual(MAX_WINDOW_SHUTTER, device.type)
        self.assertEqual('KEQ0839778', device.serial)
        self.assertEqual(1, device.room_id)

    def test_device_by_rf_negative(self):
        device = self.cube.device_by_rf('DEADBEEF')

        self.assertEqual(None, device)

    def test_devices_by_room(self):
        room = MaxRoom()
        room.id = 1
        devices = self.cube.devices_by_room(room)
        self.assertEqual(2, len(devices))

    def test_devices_by_room_negative(self):
        room = MaxRoom()
        room.id = 3
        devices = self.cube.devices_by_room(room)
        self.assertEqual(0, len(devices))

    def test_get_rooms(self):
        rooms = self.cube.get_rooms()
    
        self.assertEqual('Badezimmer', rooms[0].name)
        self.assertEqual(1, rooms[0].id)

        self.assertEqual('Wohnzimmer', rooms[1].name)
        self.assertEqual(2, rooms[1].id)

    def test_room_by_id(self):
        room = self.cube.room_by_id(1)
        
        self.assertEqual('Badezimmer', room.name)
        self.assertEqual(1, room.id)

    def test_room_by_id_negative(self):
        room = self.cube.room_by_id(3)

        self.assertEqual(None, room)
