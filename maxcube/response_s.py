from maxcube.response import MaxResponse

class MaxResponseS(MaxResponse):
    def __init__(self):
        super(MaxResponse, self).__init__()
        self.duty_cycle = None
        self.result = None
        self.free_memory_slots = None

