from maxcube.device import MaxDevice
from time import localtime
from typing import Dict, List

PROG_DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

class MaxThermostat(MaxDevice):
    def __init__(self):
        super(MaxThermostat, self).__init__()
        self.comfort_temperature = None
        self.eco_temperature = None
        self.max_temperature = None
        self.min_temperature = None
        self.valve_position = None
        self.target_temperature = None
        self.actual_temperature = None
        self.mode = None
        self.programme: Dict[str, List[Dict[str, int]]] = {}

    def get_current_temp_in_auto_mode(self):
        t = localtime()
        weekday = PROG_DAYS[t.tm_wday]
        time = f"{t.tm_hour:02}:{t.tm_min:02}"
        for point in self.programme.get(weekday, []):
            if time < point['until']:
                return point['temp']
        return None
