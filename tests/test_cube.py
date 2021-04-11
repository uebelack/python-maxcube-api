from datetime import datetime
from typing import List
from unittest import TestCase
from unittest.mock import patch

from maxcube.cube import MaxCube
from maxcube.device import (
    MAX_CUBE,
    MAX_DEVICE_BATTERY_LOW,
    MAX_DEVICE_MODE_AUTOMATIC,
    MAX_DEVICE_MODE_MANUAL,
    MAX_THERMOSTAT,
    MAX_THERMOSTAT_PLUS,
    MAX_WALL_THERMOSTAT,
    MAX_WINDOW_SHUTTER,
    MaxDevice,
)
from maxcube.message import Message
from maxcube.room import MaxRoom


def to_messages(lines):
    return [Message.decode(line) for line in lines]


INIT_RESPONSE_1 = to_messages(
    [
        b"H:KEQ0566338,0b6475,0113,00000000,74b7b6f7,00,32,0f0c19,1527,03,0000",
        b"M:00,01,VgIEAQdLaXRjaGVuBrxTAgZMaXZpbmcGvFoDCFNsZWVwaW5nCKuCBARXb3JrBrxcBAEGvFNLRVEwMzM2MTA4B0tpdGNoZW4BAQa8Wk"
        b"tFUTAzMzYxMDAGTGl2aW5nAgEIq4JLRVEwMzM1NjYyCFNsZWVwaW5nAwEGvFxLRVEwMzM2MTA0BFdvcmsEAQ==",
        b"C:0b6475,7QtkdQATAf9LRVEwNTY2MzM4AQsABEAAAAAAAAAAAP///////////////////////////wsABEAAAAAAAAAAQf////////////////"
        b"///////////2h0dHA6Ly93d3cubWF4LXBvcnRhbC5lbHYuZGU6ODAvY3ViZQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        b"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAENFVAAACgADAAAOEENFU1QAAwACAAAcIA==",
        b"C:06bc53,0ga8UwEBGP9LRVEwMzM2MTA4KCEyCQcYAzAM/wBESFUIRSBFIEUgRSBFIEUgRSBFIEUgRSBFIERIVQhFIEUgRSBFIEUgRSBFIEUgRS"
        b"BFIEUgREhUbETMVRRFIEUgRSBFIEUgRSBFIEUgRSBESFRsRMxVFEUgRSBFIEUgRSBFIEUgRSBFIERIVGxEzFUURSBFIEUgRSBFIEUgRSBFIEUgR"
        b"EhUbETMVRRFIEUgRSBFIEUgRSBFIEUgRSBESFRsRMxVFEUgRSBFIEUgRSBFIEUgRSBFIA==",
        b"C:06bc5a,0ga8WgECGP9LRVEwMzM2MTAwKCEyCQcYAzAM/wBESFUIRSBFIEUgRSBFIEUgRSBFIEUgRSBFIERIVQhFIEUgRSBFIEUgRSBFIEUgRS"
        b"BFIEUgREhUbETMVRRFIEUgRSBFIEUgRSBFIEUgRSBESFRsRMxVFEUgRSBFIEUgRSBFIEUgRSBFIERIVGxEzFUURSBFIEUgRSBFIEUgRSBFIEUgR"
        b"EhUbETMVRRFIEUgRSBFIEUgRSBFIEUgRSBESFRsRMxVFEUgRSBFIEUgRSBFIEUgRSBFIA==",
        b"C:06bc5c,0ga8XAEEGP9LRVEwMzM2MTA0KCEyCQcYAzAM/wBESFUIRSBFIEUgRSBFIEUgRSBFIEUgRSBFIERIVQhFIEUgRSBFIEUgRSBFIEUgR"
        b"SBFIEUgREhUbETMVRRFIEUgRSBFIEUgRSBFIEUgRSBESFRsRMxVFEUgRSBFIEUgRSBFIEUgRSBFIERIVGxEzFUURSBFIEUgRSBFIEUgRSBFIEU"
        b"gREhUbETMVRRFIEUgRSBFIEUgRSBFIEUgRSBESFRsRMxVFEUgRSBFIEUgRSBFIEUgRSBFIA==",
        b"C:08ab82,0girggEDGP9LRVEwMzM1NjYyKCEyCQcYAzAM/wBEYFRsRMxFFEUgRSBFIEUgRSBFIEUgRSBFIERgVGxEzEUURSBFIEUgRSBFIEUgR"
        b"SBFIEUgRGBUbETMRRRFIEUgRSBFIEUgRSBFIEUgRSBEYFRsRMxFFEUgRSBFIEUgRSBFIEUgRSBFIERgVGxEzEUURSBFIEUgRSBFIEUgRSBFIEU"
        b"gRGBUbETMRRRFIEUgRSBFIEUgRSBFIEUgRSBEYFRsRMxFFEUgRSBFIEUgRSBFIEUgRSBFIA==",
        b"L:Cwa8U/EaGBsqAOwACwa8WgkSGCMqAOcACwa8XAkSGAsqAOcACwirggMaGAAiAAAA",
    ]
)

INIT_RESPONSE_2 = to_messages(
    [
        b"H:JEQ0341267,015d2a,0113,00000000,0336f10a,4b,29,110203,172a,03,0000",
        b"M:00,01,VgICAQpCYWRlemltbWVyDi66AgpXb2huemltbWVyAAAAAwEOLrpLRVExMDg2NDM3ClRoZXJtb3N0YXQBAwoIgUtFUTA2NTU3NDMOV2"
        b"FuZHRoZXJtb3N0YXQCBAyisktFUTA4Mzk3NzgORmVuc3RlcmtvbnRha3QBAQ==",
        b"C:015d2a,7QFdKgATAf9KRVEwMzQxMjY3AQsABEAAAAAAAAAAAP///////////////////////////wsABEAAAAAAAAAAQf///////////////"
        b"////////////2h0dHA6Ly9tYXguZXEtMy5kZTo4MC9jdWJlADAvbG9va3VwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        b"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAENFVAAACgADAAAOEENFU1QAAwACAAAcIA==",
        b"C:0a0881,zgoIgQMCEP9LRVEwNjU1NzQzKyE9CURIVQhFIEUgRSBFIEUgRSBFIEUgRSBFIEUgREhVCEUgRSBFIEUgRSBFIEUgRSBFIEUgRSBES"
        b"FRsRMxVFEUgRSBFIEUgRSBFIEUgRSBFIERIVGxEzFUURSBFIEUgRSBFIEUgRSBFIEUgREhUbETMVRRFIEUgRSBFIEUgRSBFIEUgRSBESFRsRMx"
        b"VFEUgRSBFIEUgRSBFIEUgRSBFIERIVGxEzFUURSBFIEUgRSBFIEUgRSBFIEUgBxgw",
        b"C:0ca2b2,EQyisgQBFA9LRVEwODM5Nzc4",
        b"C:0e2eba,0g4uugEBEKBLRVExMDg2NDM3KyE9CQcYAzAM/wAgYFR4ISAhICEgISAhIEUgRSBFIEUgRSBFICBgVHghICEgISAhICEgRSBFIEUgR"
        b"SBFIEUgIEJUTiEfISAhICEgISBFIEUgRSBFIEUgRSAgQlROIR8hICEgISAhIEUgRSBFIEUgRSBFICBCVE4hHyEgISAhICEgRSBFIEUgRSBFIEU"
        b"gIEJUTiEfISAhICEgISBFIEUgRSBFIEUgRSAgQlROIR8hICEgISAhIEUgRSBFIEUgRSBFIA==",
        b"L:DAoIgewSGAQQAAAA5QYMorL3EpALDi66ChIYABAAAAA=",
    ]
)

LAST_STATE_MSG = Message.decode(
    b"L:Cwa8U/ESGAAiAAAACwa8WgkSGAAiAAAACwa8XAkSGAUiAAAACwirggMSGAUiAAAA"
)

SEND_CMD_OK_RESPONSE = "S:04,0,31"

WORKDAY_PROGRAMME_1 = [
    {"until": "05:30", "temp": 8},
    {"until": "06:30", "temp": 21},
    {"until": "23:55", "temp": 8},
    {"until": "24:00", "temp": 8},
]

WEEKEND_PROGRAME_1 = [
    {"until": "08:00", "temp": 8},
    {"until": "10:00", "temp": 21},
    {"until": "24:00", "temp": 8},
]

INIT_PROGRAMME_1 = {
    "monday": WORKDAY_PROGRAMME_1,
    "tuesday": WORKDAY_PROGRAMME_1,
    "wednesday": WORKDAY_PROGRAMME_1,
    "thursday": WORKDAY_PROGRAMME_1,
    "friday": WORKDAY_PROGRAMME_1,
    "saturday": WEEKEND_PROGRAME_1,
    "sunday": WEEKEND_PROGRAME_1,
}


@patch("maxcube.cube.Commander", spec=True)
class TestMaxCube(TestCase):
    """ Test the Max! Cube. """

    def init(self, ClassMock, responses):
        self.commander = ClassMock.return_value
        self.commander.update.return_value = responses

        self.cube = MaxCube("host", 1234, now=lambda: datetime(2012, 10, 22, 5, 30))

        self.commander.update.assert_called_once()
        self.commander.update.reset_mock()
        self.commander.send_radio_msg.return_value = True

    def test_init(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_1)
        self.assertEqual("KEQ0566338", self.cube.serial)
        self.assertEqual("0b6475", self.cube.rf_address)
        self.assertEqual("Cube", self.cube.name)
        self.assertEqual("01.13", self.cube.firmware_version)
        self.assertEqual(4, len(self.cube.devices))

        device = self.cube.devices[0]
        self.assertEqual(4.5, device.min_temperature)
        self.assertEqual(25.0, device.max_temperature)
        self.assertEqual("06BC53", device.rf_address)
        self.assertEqual("Kitchen", device.name)

        self.assertEqual("06BC5A", self.cube.devices[1].rf_address)
        self.assertEqual("Living", self.cube.devices[1].name)

        self.assertEqual("08AB82", self.cube.devices[2].rf_address)
        self.assertEqual("Sleeping", self.cube.devices[2].name)

        self.assertEqual("06BC5C", self.cube.devices[3].rf_address)
        self.assertEqual("Work", self.cube.devices[3].name)

    def __update(self, responses: List[Message]):
        self.commander.update.return_value = responses
        self.cube.update()
        self.commander.update.assert_called_once()

    def test_parse_auto_l_message(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_1)
        self.__update([LAST_STATE_MSG])

        device = self.cube.devices[0]
        self.assertEqual(MAX_DEVICE_MODE_AUTOMATIC, device.mode)
        self.assertEqual(23.6, device.actual_temperature)
        self.assertEqual(17.0, device.target_temperature)

    def test_parse_manual_l_message(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_1)
        self.__update(
            [
                Message.decode(
                    b"L:Cwa8U/ESGQkhALMACwa8WgkSGQAhAMAACwa8XAkSGQUhALIACwirggMSGQUhAAAA"
                )
            ]
        )

        device = self.cube.devices[0]
        self.assertEqual(MAX_DEVICE_MODE_MANUAL, device.mode)
        self.assertEqual(17.9, device.actual_temperature)
        self.assertEqual(16.5, device.target_temperature)

    def test_disconnect(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_1)
        self.cube.disconnect()
        self.commander.disconnect.assert_called_once()

    def test_use_persistent_connection(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_1)
        self.commander.use_persistent_connection = True
        self.assertTrue(self.cube.use_persistent_connection)
        self.cube.use_persistent_connection = False
        self.assertFalse(self.commander.use_persistent_connection)

    def test_is_thermostat(self, _):
        device = MaxDevice()
        device.type = MAX_CUBE
        self.assertFalse(device.is_thermostat())
        device.type = MAX_THERMOSTAT
        self.assertTrue(device.is_thermostat())
        device.type = MAX_THERMOSTAT_PLUS
        self.assertTrue(device.is_thermostat())
        device.type = MAX_WALL_THERMOSTAT
        self.assertFalse(device.is_thermostat())
        device.type = MAX_WINDOW_SHUTTER
        self.assertFalse(device.is_thermostat())

    def test_is_wall_thermostat(self, _):
        device = MaxDevice()
        device.type = MAX_CUBE
        self.assertFalse(device.is_wallthermostat())
        device.type = MAX_THERMOSTAT
        self.assertFalse(device.is_wallthermostat())
        device.type = MAX_THERMOSTAT_PLUS
        self.assertFalse(device.is_wallthermostat())
        device.type = MAX_WALL_THERMOSTAT
        self.assertTrue(device.is_wallthermostat())
        device.type = MAX_WINDOW_SHUTTER
        self.assertFalse(device.is_wallthermostat())

    def test_is_window_shutter(self, _):
        device = MaxDevice()
        device.type = MAX_CUBE
        self.assertFalse(device.is_windowshutter())
        device.type = MAX_THERMOSTAT
        self.assertFalse(device.is_windowshutter())
        device.type = MAX_THERMOSTAT_PLUS
        self.assertFalse(device.is_windowshutter())
        device.type = MAX_WALL_THERMOSTAT
        self.assertFalse(device.is_windowshutter())
        device.type = MAX_WINDOW_SHUTTER
        self.assertTrue(device.is_windowshutter())

    def test_set_target_temperature(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_1)

        self.assertTrue(self.cube.set_target_temperature(self.cube.devices[0], 24.5))

        self.assertEqual(24.5, self.cube.devices[0].target_temperature)
        self.commander.send_radio_msg.assert_called_once()
        self.commander.send_radio_msg.assert_called_with("00044000000006BC530131")

    def test_do_not_update_if_set_target_temperature_fails(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_1)
        self.commander.send_radio_msg.return_value = False

        self.assertFalse(self.cube.set_target_temperature(self.cube.devices[0], 24.5))

        self.assertEqual(21, self.cube.devices[0].target_temperature)
        self.commander.send_radio_msg.assert_called_once()
        self.commander.send_radio_msg.assert_called_with("00044000000006BC530131")

    def test_set_target_temperature_should_round_temperature(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_1)

        self.cube.set_target_temperature(self.cube.devices[0], 24.6)

        self.assertEqual(24.5, self.cube.devices[0].target_temperature)
        self.commander.send_radio_msg.assert_called_once()
        self.commander.send_radio_msg.assert_called_with("00044000000006BC530131")

    def test_set_target_temperature_is_ignored_by_windowshutter(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_2)
        self.cube.set_target_temperature(self.cube.devices[2], 24.5)
        self.commander.send_radio_msg.assert_not_called()

    def test_set_mode_thermostat(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_1)
        device = self.cube.devices[0]
        self.assertEqual(21.0, device.target_temperature)
        self.cube.set_mode(device, MAX_DEVICE_MODE_MANUAL)

        self.assertEqual(MAX_DEVICE_MODE_MANUAL, device.mode)
        self.commander.send_radio_msg.assert_called_once()
        self.commander.send_radio_msg.assert_called_with("00044000000006BC53016A")

    def test_init_2(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_2)
        self.assertEqual("JEQ0341267", self.cube.serial)
        self.assertEqual("015d2a", self.cube.rf_address)
        self.assertEqual("Cube", self.cube.name)
        self.assertEqual("01.13", self.cube.firmware_version)
        self.assertEqual(3, len(self.cube.devices))

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

        device = self.cube.devices[0]
        self.assertEqual(MAX_DEVICE_MODE_AUTOMATIC, device.mode)
        self.assertIsNone(device.actual_temperature)
        self.assertEqual(8.0, device.target_temperature)

        device = self.cube.devices[1]
        self.assertEqual(MAX_DEVICE_MODE_AUTOMATIC, device.mode)
        self.assertEqual(22.9, device.actual_temperature)
        self.assertEqual(8.0, device.target_temperature)

        device = self.cube.devices[2]
        self.assertFalse(device.is_open)
        self.assertTrue(device.battery == MAX_DEVICE_BATTERY_LOW)

    def test_parse_m_message(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_2)
        self.__update(
            [
                Message.decode(
                    b"M:00,01,VgIEAQdLaXRjaGVuBrxTAgZMaXZpbmcGvFoDCFNsZWVwaW5nCKuCBARXb3JrBrxcBAEGvF"
                    b"NLRVEwMzM2MTA4B0tpdGNoZW4BAQa8WktFUTAzMzYxMDAGTGl2aW5nAgEIq4JLRVEwMzM1NjYyCFNs"
                    b"ZWVwaW5nAwEGvFxLRVEwMzM2MTA0BFdvcmsEAQ=="
                ),
                INIT_RESPONSE_2[-1],
            ]
        )

        self.assertEqual("0E2EBA", self.cube.devices[0].rf_address)
        self.assertEqual("Thermostat", self.cube.devices[0].name)
        self.assertEqual(MAX_THERMOSTAT, self.cube.devices[0].type)
        self.assertEqual("KEQ1086437", self.cube.devices[0].serial)
        self.assertEqual(1, self.cube.devices[0].room_id)

        self.assertEqual("0A0881", self.cube.devices[1].rf_address)
        self.assertEqual("Wandthermostat", self.cube.devices[1].name)
        self.assertEqual(MAX_WALL_THERMOSTAT, self.cube.devices[1].type)
        self.assertEqual("KEQ0655743", self.cube.devices[1].serial)
        self.assertEqual(2, self.cube.devices[1].room_id)

        self.assertEqual("0CA2B2", self.cube.devices[2].rf_address)
        self.assertEqual("Fensterkontakt", self.cube.devices[2].name)
        self.assertEqual(MAX_WINDOW_SHUTTER, self.cube.devices[2].type)
        self.assertEqual("KEQ0839778", self.cube.devices[2].serial)
        self.assertEqual(1, self.cube.devices[2].room_id)

        self.assertEqual("Kitchen", self.cube.rooms[0].name)
        self.assertEqual(1, self.cube.rooms[0].id)

        self.assertEqual("Living", self.cube.rooms[1].name)
        self.assertEqual(2, self.cube.rooms[1].id)

    def test_get_devices(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_2)
        devices = self.cube.get_devices()
        self.assertEqual(3, len(devices))

    def test_device_by_rf(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_2)
        device = self.cube.device_by_rf("0CA2B2")

        self.assertEqual("0CA2B2", device.rf_address)
        self.assertEqual("Fensterkontakt", device.name)
        self.assertEqual(MAX_WINDOW_SHUTTER, device.type)
        self.assertEqual("KEQ0839778", device.serial)
        self.assertEqual(1, device.room_id)

    def test_device_by_rf_negative(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_2)
        device = self.cube.device_by_rf("DEADBEEF")

        self.assertIsNone(device)

    def test_devices_by_room(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_2)
        room = MaxRoom()
        room.id = 1
        devices = self.cube.devices_by_room(room)
        self.assertEqual(2, len(devices))

    def test_devices_by_room_negative(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_2)
        room = MaxRoom()
        room.id = 3
        devices = self.cube.devices_by_room(room)
        self.assertEqual(0, len(devices))

    def test_get_rooms(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_2)
        rooms = self.cube.get_rooms()

        self.assertEqual("Badezimmer", rooms[0].name)
        self.assertEqual(1, rooms[0].id)

        self.assertEqual("Wohnzimmer", rooms[1].name)
        self.assertEqual(2, rooms[1].id)

    def test_room_by_id(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_2)
        room = self.cube.room_by_id(1)

        self.assertEqual("Badezimmer", room.name)
        self.assertEqual(1, room.id)

    def test_room_by_id_negative(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_2)
        room = self.cube.room_by_id(3)

        self.assertIsNone(room)

    def test_set_programme(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_2)
        self.commander.send_radio_msg.return_value = True
        result = self.cube.set_programme(
            self.cube.devices[0],
            "saturday",
            [{"temp": 20.5, "until": "13:30"}, {"temp": 18, "until": "24:00"}],
        )
        self.assertTrue(result)
        self.commander.send_radio_msg.assert_called_once()
        self.commander.send_radio_msg.assert_called_with(
            "0000100000000E2EBA010052A249200000000000"
        )

    def test_set_programme_already_existing_does_nothing(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_2)
        result = self.cube.set_programme(
            self.cube.devices[0], "saturday", INIT_PROGRAMME_1["saturday"]
        )
        self.assertIsNone(result)
        self.commander.send_radio_msg.assert_not_called()

    def test_get_device_as_dict(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_2)
        device = self.cube.devices[0]
        result = device.to_dict()
        self.assertEqual(result["name"], "Thermostat")
        self.assertEqual(result["comfort_temperature"], 21.5)
        self.assertEqual(
            result["programme"]["monday"],
            [
                {"until": "05:30", "temp": 8},
                {"until": "06:30", "temp": 21},
                {"until": "23:55", "temp": 8},
                {"until": "24:00", "temp": 8},
            ],
        )

    def test_set_auto_mode_read_temp_from_program(self, ClassMock):
        self.init(ClassMock, INIT_RESPONSE_2)
        device = self.cube.devices[0]
        self.assertEqual(8.0, device.target_temperature)
        self.cube.set_mode(device, MAX_DEVICE_MODE_AUTOMATIC)
        self.assertEqual(21.0, device.target_temperature)
        self.assertEqual(MAX_DEVICE_MODE_AUTOMATIC, device.mode)
        self.commander.send_radio_msg.assert_called_once()
        self.commander.send_radio_msg.assert_called_with("0004400000000E2EBA0100")
