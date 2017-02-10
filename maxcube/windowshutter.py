from maxcube.device import MaxDevice


class MaxWindowShutter(MaxDevice):
    def __init__(self):
        super(MaxWindowShutter, self).__init__()
        self.is_open = False
        self.initialized = None
