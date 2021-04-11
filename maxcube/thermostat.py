from datetime import datetime
from typing import Dict, List

from maxcube.device import MODE_NAMES, MaxDevice

PROG_DAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


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

    def __str__(self):
        return self.describe(
            "THERMOSTAT",
            f"mode={MODE_NAMES.get(self.mode, str(self.mode))}",
            f"actual={self.actual_temperature}",
            f"target={self.target_temperature}",
            f"eco={self.eco_temperature}",
            f"comfort={self.comfort_temperature}",
            f"range=[{self.min_temperature},{self.max_temperature}]",
            f"valve={self.valve_position}",
        )

    def get_programmed_temp_at(self, dt: datetime):
        """Retrieve the programmed temperature at the given instant."""
        weekday = PROG_DAYS[dt.weekday()]
        time = f"{dt.hour:02}:{dt.minute:02}"
        for point in self.programme.get(weekday, []):
            if time < point["until"]:
                return point["temp"]
        return None

    def get_current_temp_in_auto_mode(self):
        """DEPRECATED: use get_programmed_temp_at instead."""
        return self.get_programmed_temp_at(datetime.now())
