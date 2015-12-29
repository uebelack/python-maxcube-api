from maxcube.device import MaxDevice


class MaxThermostat(MaxDevice):
    def __init__(self):
        super().__init__()
        self.mode = None
        self.min_temperature = None
        self.max_temperature = None
        self.actual_temperature = None
        self.target_temperature = None
