MAX_CUBE = 0
MAX_THERMOSTAT = 1
MAX_THERMOSTAT_PLUS = 2
MAX_WALL_THERMOSTAT = 3
MAX_WINDOW_SHUTTER = 4
MAX_PUSH_BUTTON = 5

MAX_DEVICES = [
        "cube",
        "thermostat",
        "thermostat_plus",
        "wall_thermostat",
        "window_shutter",
        "push_button"
]

MAX_DEVICE_MODE_AUTOMATIC = 0
MAX_DEVICE_MODE_MANUAL = 1
MAX_DEVICE_MODE_VACATION = 2
MAX_DEVICE_MODE_BOOST = 3

MAX_DEVICE_MODES = [
        "auto",
        "manual",
        "vacation",
        "boost"
]

class MaxDevice(object):
    def __init__(self):
        self.cube = None
        self.type = None
        self.type_name = None
        self.rf_address = None
        self.room_id = None
        self.name = None

    def todict(self):
        d = {
                "type": self.type_name,
                "rf_address": self.rf_address,
                "room_id": self.room_id,
                "name": self.name
        }
        return d
