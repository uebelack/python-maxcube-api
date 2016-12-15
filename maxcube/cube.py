import base64
import struct

from maxcube.device import \
    MaxDevice, \
    MAX_CUBE, \
    MAX_THERMOSTAT, \
    MAX_THERMOSTAT_PLUS, \
    MAX_DEVICE_MODE_AUTOMATIC, \
    MAX_DEVICE_MODE_MANUAL, \
    MAX_DEVICE_MODE_VACATION, \
    MAX_DEVICE_MODE_BOOST

from maxcube.thermostat import MaxThermostat
import logging

logger = logging.getLogger(__name__)


class MaxCube(MaxDevice):
    def __init__(self, connection):
        super(MaxCube, self).__init__()
        self.connection = connection
        self.name = 'Cube'
        self.type = MAX_CUBE
        self.firmware_version = None
        self.devices = []
        self.init()

    def init(self):
        self.update()
        self.log()
        
    def log(self):
        logger.info('Cube (rf=%s, firmware=%s)' % (self.rf_address, self.firmware_version))
        for device in self.devices:
            if self.is_thermostat(device):
                logger.info('Thermostat (type=%s, rf=%s, room=%s, name=%s, mode=%s, min=%s, max=%s, actual=%s, target=%s)'
                            % (device.type, device.rf_address, device.room_id, device.name, device.mode, device.min_temperature,
                               device.max_temperature, device.actual_temperature,
                               device.target_temperature))
            else:
                logger.info('Device (rf=%s, name=%s' % (device.rf_address, device.name))

    def update(self):
        self.connection.connect()
        response = self.connection.response
        self.parse_response(response)
        self.connection.disconnect()
    
    def get_devices(self):
        return self.devices

    def device_by_rf(self, rf):
        for device in self.devices:
            if device.rf_address == rf:
                return device
        return None

    def parse_response(self, response):
        try:
            lines = unicode.split(unicode(response), '\n')
        except:
            lines = str.split(response, '\n')


        for line in lines:
            line = line.strip()
            if line and len(line) > 10:
                if line[:1] == 'C':
                    self.parse_c_message(line.strip())
                elif line[:1] == 'H':
                    self.parse_h_message(line.strip())
                elif line[:1] == 'L':
                    self.parse_l_message(line.strip())
                elif line[:1] == 'M':
                    self.parse_m_message(line.strip())

    def parse_c_message(self, message):
        logger.debug('Parsing c_message: ' + message)
        device_rf_address = message[1:].split(',')[0][1:].upper()
        data = bytearray(base64.b64decode(message[2:].split(',')[1]))
        device = self.device_by_rf(device_rf_address)

        if device and self.is_thermostat(device):
            device.min_temperature = data[21] / 2.0
            device.max_temperature = data[20] / 2.0

    def parse_h_message(self, message):
        logger.debug('Parsing h_message: ' + message)
        tokens = message[2:].split(',')
        self.rf_address = tokens[1]
        self.firmware_version = (tokens[2][0:2]) + '.' + (tokens[2][2:4])

    def parse_m_message(self, message):
        logger.debug('Parsing m_message: ' + message)
        data = bytearray(base64.b64decode(message[2:].split(',')[2]))
        num_rooms = data[2]

        pos = 3
        for _ in range(0, num_rooms):
            room_id = struct.unpack('bb', data[pos:pos + 2])[0]
            name_length = struct.unpack('bb', data[pos:pos + 2])[1]
            pos += 1 + 1
            name = data[pos:pos + name_length].decode('utf-8')
            pos += name_length
            device_rf_address = self.parse_rf_address(data[pos: pos + 3])
            pos += 3
        
        num_devices = data[pos]
        pos += 1

        for device_idx in range(0, num_devices):
            device_type = data[pos]
            device_rf_address = self.parse_rf_address(data[pos + 1: pos + 1 + 3])
            device_name_length = data[pos + 14]
            device_name = data[pos + 15:pos + 15 + device_name_length].decode('utf-8')
            room_id = data[pos + 15 + device_name_length]

            device = self.device_by_rf(device_rf_address)

            if not device:
                if device_type == MAX_THERMOSTAT or device_type == MAX_THERMOSTAT_PLUS:
                    device = MaxThermostat()

                if device:
                    self.devices.append(device)
            
            if device:
                device.type = device_type
                device.rf_address = device_rf_address
                device.room_id = room_id
                device.name = device_name

            pos += 1 + 3 + 10 + device_name_length + 2

    def parse_l_message(self, message):
        logger.debug('Parsing l_message: ' + message)
        data = bytearray(base64.b64decode(message[2:]))
        pos = 0

        while pos < len(data):
            length = data[pos]
            pos += 1
            device_rf_address = self.parse_rf_address(data[pos: pos + 3])
            
            device = self.device_by_rf(device_rf_address)

            if device and self.is_thermostat(device):
                device.rf_address = device_rf_address
                bits1, bits2 = struct.unpack('BB', bytearray(data[pos + 4:pos + 6]))
                device.mode = self.resolve_device_mode(bits2)
                if device.mode == MAX_DEVICE_MODE_MANUAL or device.mode == MAX_DEVICE_MODE_AUTOMATIC:
                    actual_temperature = ((data[pos + 8] & 0xFF) * 256 + (data[pos + 9] & 0xFF)) / 10.0
                    if actual_temperature != 0:
                        device.actual_temperature = actual_temperature
                else:
                    device.actual_temperature = None
                device.target_temperature = (data[pos + 7] & 0x7F) / 2.0
            pos += length

    def set_target_temperature(self, thermostat, temperature):
        logger.debug('Setting temperature for %s to %s!' %(thermostat.rf_address, temperature))
        rf_address = thermostat.rf_address
        room = str(thermostat.room_id)
        if thermostat.room_id < 10:
            room = '0' + room
        target_temperature = int(temperature * 2) + (thermostat.mode << 6)

        byte_cmd = '000440000000' + rf_address + room + hex(target_temperature)[2:]
        logger.debug('Request: ' + byte_cmd)
        command = 's:' + base64.b64encode(bytearray.fromhex(byte_cmd)).decode('utf-8') + '\r\n'
        logger.debug('Command: ' + command)

        self.connection.connect()
        self.connection.send(command)
        logger.debug('Response: ' + self.connection.response)
        self.connection.disconnect()
        thermostat.target_temperature = int(temperature * 2) / 2.0

    @classmethod
    def resolve_device_mode(cls, bits):
        return (bits & 3)

    @classmethod
    def is_thermostat(cls, device):
        return device.type == MAX_THERMOSTAT or device.type == MAX_THERMOSTAT_PLUS

    @classmethod
    def parse_rf_address(cls, address):
        return ''.join('{:02X}'.format(x)  for x in address)
