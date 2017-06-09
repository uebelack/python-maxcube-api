import base64
from maxcube.device import MaxDevice


class MaxThermostat(MaxDevice):
    def __init__(self):
        super(MaxThermostat, self).__init__()
        self.mode = None
        self.mode_name = None
        self.min_temperature = None
        self.max_temperature = None
        self.actual_temperature = None
        self.target_temperature = None
        self.valve_position = None

    def todict(self):
        d = super(MaxThermostat, self).todict()
        h = {
                "mode": self.mode_name,
                "mode_id": self.mode,
                "min_temperature": self.min_temperature,
                "max_temperature": self.max_temperature,
                "actual_temperature": self.actual_temperature,
                "target_temperature": self.target_temperature,
                "valve_position": self.valve_position
                }
        return { **d, **h }


    def set_temperature(self, temperature, mode="manual"):
        self.cube.logger.debug('Setting temperature for %s to %s!' %(self.rf_address, temperature))
        mode_id = MAX_DEVICE_MODES.index(mode)
        rf_address = self.rf_address
        if len(rf_address) < 6:
            rf_address = '0' + rf_address
        room = str(self.room_id)
        if self.room_id < 10:
            room = '0' + room
        target_temperature = int(temperature * 2) + (mode_id << 6)

        byte_cmd = '000440000000' + rf_address + room + hex(target_temperature)[2:]
        self.cube.logger.debug('Request: ' + byte_cmd)
        command = 's:' + base64.b64encode(bytearray.fromhex(byte_cmd)).decode('utf-8') + '\r\n'
        self.cube.logger.debug('Command: ' + command)

        self.cube.connection.connect()
        self.cube.connection.send(command)
        self.cube.logger.debug('Response: ' + self.cube.connection.response)
        a = self.cube.parse_s_message(self.cube.connection.response)
        self.cube.connection.disconnect()
        if a.result:
            self.target_temperature = int(temperature * 2) / 2.0
        a.device = self
        return a
