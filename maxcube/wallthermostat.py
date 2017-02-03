from maxcube.device import MaxDevice


class MaxWallThermostat(MaxDevice):
    def __init__(self):
        super(MaxWallThermostat, self).__init__()
        self.comfort_temperature = None
        self.eco_temperature = None
        self.max_temperature = None
        self.min_temperature = None
        self.actual_temperature = None
        self.target_temperature = None
        self.mode = None
