from typing import Tuple

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

MAX_DEVICE_PANEL_UNLOCKED = 0
MAX_DEVICE_PANEL_LOCKED = 1

MAX_DEVICE_LINK_STATUS_OK = 0
MAX_DEVICE_LINK_STATUS_ERROR = 1

MAX_DEVICE_STATUS_NOT_INITIALIZED = 0
MAX_DEVICE_STATUS_INITIALIZED = 1

MAX_DEVICE_ERROR_NO = 0
MAX_DEVICE_ERROR_YES = 1

MODE_NAMES = {
    MAX_DEVICE_MODE_AUTOMATIC: "auto",
    MAX_DEVICE_MODE_MANUAL: "manual",
    MAX_DEVICE_MODE_VACATION: "away",
    MAX_DEVICE_MODE_BOOST: "boost",
}


class MaxDevice(object):
    def __init__(self):
        self.type = None
        self.rf_address = None
        self.room_id = None
        self.name = None
        self.serial = None
        self.panel_locked = None
        self.link_status = None
        self.status_inited = None
        self.error = None
        self.battery = None
        self.programme = None

    def is_thermostat(self):
        return self.type in (MAX_THERMOSTAT, MAX_THERMOSTAT_PLUS)

    def is_wallthermostat(self):
        return self.type == MAX_WALL_THERMOSTAT

    def is_windowshutter(self):
        return self.type == MAX_WINDOW_SHUTTER

    def is_room(self):
        return False

    def describe(self, kind: str, *args: Tuple[str]):
        state = "".join("," + s for s in args if s)
        if self.battery == MAX_DEVICE_BATTERY_LOW:
            state = ",LOW_BATT" + state
        if self.error == MAX_DEVICE_ERROR_YES:
            state = ",ERROR" + state
        if self.link_status == MAX_DEVICE_LINK_STATUS_ERROR:
            state = ",LINK_ERROR" + state
        if self.panel_locked == MAX_DEVICE_PANEL_LOCKED:
            state = ",LOCKED" + state
        if self.status_inited == MAX_DEVICE_STATUS_NOT_INITIALIZED:
            state = ",NOT_INITIALIZED" + state
        return f"{kind} sn={self.serial},rf={self.rf_address},name={self.name}" + state

    def __str__(self):
        return self.describe(str(self.type))

    def to_dict(self):
        data = {}
        keys = [
            "type",
            "rf_address",
            "room_id",
            "name",
            "serial",
            "battery",
            "comfort_temperature",
            "eco_temperature",
            "max_temperature",
            "min_temperature",
            "valve_position",
            "target_temperature",
            "actual_temperature",
            "mode",
            "programme",
        ]
        for key in keys:
            data[key] = getattr(self, key, None)
        data["rf_address"] = self.rf_address
        return data
