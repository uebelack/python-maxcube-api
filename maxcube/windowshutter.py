from maxcube.device import MaxDevice


class MaxWindowShutter(MaxDevice):
    def __init__(self):
        super(MaxWindowShutter, self).__init__()
        self.is_open = False
        self.initialized = None

    def __str__(self):
        return self.describe("WINDOW", f"open={self.is_open}")
