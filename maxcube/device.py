MAX_CUBE = 0
MAX_THERMOSTAT = 1
MAX_THERMOSTAT_PLUS = 2
MAX_WALL_THERMOSTAT = 3
MAX_WINDOW_SHUTTER = 4
MAX_PUSH_BUTTON = 5

MAX_DEVICE_MODE_AUTOMATIC = 0
MAX_DEVICE_MODE_MANUAL = 1
MAX_DEVICE_MODE_VACATION = 2
MAX_DEVICE_MODE_BOOST = 3

MAX_DEVICE_BATTERY_OK = 0
MAX_DEVICE_BATTERY_LOW = 1

class MaxDevice(object):
    def __init__(self):
        self.type = None
        self.rf_address = None
        self.room_id = None
        self.name = None
        self.serial = None
        self.battery = None
