import base64
import struct

from maxcube.device import \
    MaxDevice, \
    MAX_CUBE, \
    MAX_THERMOSTAT, \
    MAX_THERMOSTAT_PLUS, \
    MAX_DEVICES, \
    MAX_DEVICE_MODE_AUTOMATIC, \
    MAX_DEVICE_MODE_MANUAL, \
    MAX_DEVICE_MODE_VACATION, \
    MAX_DEVICE_MODE_BOOST, \
    MAX_DEVICE_MODES

from maxcube.thermostat import MaxThermostat
from maxcube.response_s import MaxResponseS
from maxcube.response_n import MaxResponseN
from maxcube.response_f import MaxResponseF
from maxcube.room import MaxRoom
import logging

logger = logging.getLogger(__name__)


class MaxCube(MaxDevice):
    def __init__(self, connection):
        super(MaxCube, self).__init__()
        self.connection = connection
        self.name = 'Cube'
        self.type = MAX_CUBE
        self.serial = None
        self.firmware_version = None
        self.duty_cycle = None
        self.free_memory_slots = None
        self.date = None
        self.time = None
        self.devices = []
        self.rooms = []
        self.logger = logger
        self.init()

    def init(self):
        self.update()
        self.log()

    def todict(self):
        d = {
                "serial": self.serial,
                "firmware_version": self.firmware_version,
                "duty_cycle": self.duty_cycle,
                "free_memory_slots": self.free_memory_slots,
                "date": self.date,
                "time": self.time
        }
        return d
        
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
        self.command()

    def command(self, command = None):
        self.connection.connect()
        if command: self.connection.send(command)
        message = self.connection.response
        response = self.parse_response(message)
        self.connection.disconnect()
        return response
    
    def get_devices(self):
        return self.devices

    def refresh_devices(self):
        self.command("l:\r\n")
        return True

    def device_by_rf(self, rf):
        for device in self.devices:
            if device.rf_address == rf:
                return device
        return None

    def room_by_id(self, id):
        for room in self.rooms:
            if room.id == id:
                return room
        return None

    def start_pairing(self, timeout = 60):
        timeout_hex = "%X" % timeout
        if timout < 256:
            timeout_hex = '00' + timeout_hex
        command = 'n:'+timeout_hex+'\r\n'
        return self.command(command)

    def ntp_servers(self, ntp = []):
        ntp_servers = ','.join(ntp)
        command = 'f:'+ntp_servers+'\r\n'
        return self.command(command)

    def wakeup(self, time = 30):
        wakeup_time = "%X" % time
        command = 'z:'+wakeup_time+'A\r\n'
        return self.command(command)

    def parse_response(self, response):
        try:
            lines = str.split(str(response), '\n')
        except:
            lines = str.split(response, '\n')


        for line in lines:
            line = line.strip()
            if line and len(line) > 1:
                if line[:1] == 'A':
                    return self.parse_a_message(line.strip())  
                elif line[:1] == 'C':
                    self.parse_c_message(line.strip())
                elif line[:1] == 'H':
                    self.parse_h_message(line.strip())
                elif line[:1] == 'L':
                    self.parse_l_message(line.strip())
                elif line[:1] == 'M':
                    self.parse_m_message(line.strip())
                elif line[:1] == 'N':
                    return self.parse_n_message(line.strip())
                elif line[:1] == 'F':
                    return self.parse_f_message(line.strip())

    def parse_a_message(self, message):
        return True

    def parse_c_message(self, message):
        logger.debug('Parsing c_message: ' + message)
        device_rf_address = message[2:].split(',')[0][1:].upper()
        data = bytearray(base64.b64decode(message[2:].split(',')[1]))
        device = self.device_by_rf(device_rf_address)

        if device and self.is_thermostat(device):
            device.min_temperature = data[21] / 2.0
            device.max_temperature = data[20] / 2.0

    def parse_h_message(self, message):
        logger.debug('Parsing h_message: ' + message)
        tokens = message[2:].split(',')
        self.serial = tokens[0]
        self.rf_address = tokens[1]
        self.firmware_version = (tokens[2][0:2]) + '.' + (tokens[2][2:4])
        self.duty_cycle = int(tokens[5], 16)
        self.free_memory_slots = int(tokens[6], 16)
        year = int(tokens[7][0:2], 16) + 2000;
        month = int(tokens[7][2:4], 16)
        day = int(tokens[7][4:6], 16)
        self.date = '%d-%d-%d' % (year, month, day)
        hour = int(tokens[8][0:2], 16)
        minute = int(tokens[8][2:4], 16)
        self.time = '%d:%d' % (hour, minute)

    def parse_s_message(self, message):
        tokens = message[2:].split(',')
        response = MaxResponseS()
        response.duty_cycle = int(tokens[0], 16)
        self.duty_cyle = response.duty_cycle
        response.result = tokens[1] == '0'
        response.free_memory_slots = int(tokens[2].strip(), 16)
        self.free_memory_slots = response.free_memory_slots
        return response

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
            device_rf_address = ''.join("%X" % x for x in data[pos: pos + 3])
            pos += 3

            room = MaxRoom()
            room.id = room_id
            room.name = name
            room.rf_address = device_rf_address
            self.rooms.append(room)
        
        num_devices = data[pos]
        pos += 1

        for device_idx in range(0, num_devices):
            device_type = data[pos]
            device_rf_address = ''.join("%X" % x for x in data[pos + 1: pos + 1 + 3])
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
                device.cube = self
                device.type = device_type
                device.type_name = MAX_DEVICES[device_type]
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
            device_rf_address = ''.join("%X" % x for x in data[pos: pos + 3])
            
            device = self.device_by_rf(device_rf_address)

            if device and self.is_thermostat(device):
                device.rf_address = device_rf_address
                bits1, bits2 = struct.unpack('BB', bytearray(data[pos + 4:pos + 6]))
                device.mode = self.resolve_device_mode(bits2)
                device.mode_name = MAX_DEVICE_MODES[self.resolve_device_mode(bits2)]
                device.valve_position = data[pos + 6] & 0xFF
                if device.mode == MAX_DEVICE_MODE_MANUAL or device.mode == MAX_DEVICE_MODE_AUTOMATIC:
                    actual_temperature = ((data[pos + 8] & 0xFF) * 256 + (data[pos + 9] & 0xFF)) / 10.0
                    if actual_temperature != 0:
                        device.actual_temperature = actual_temperature
                else:
                    device.actual_temperature = None
                device.target_temperature = (data[pos + 7] & 0x7F) / 2.0
            pos += length

    def parse_n_message(self, message):
        data = bytearray(base64.b64decode(message[2:]))
        pos = 0
        response = MaxResponseN()
        response.device_type = int(data[pos])
        pos += 1
        response.rf_address = ''.join("%X" % x for x in data[pos: pos + 3])
        pos += 3
        response.serial = data[pos:pos + 10]
        return response

    def parse_f_message(self, message):
        tokens = message[2:].split(',')
        response = MaxResponseF()
        response.ntp_servers = tokens
        return response

    @classmethod
    def resolve_device_mode(cls, bits):
        return (bits & 3)

    @classmethod
    def is_thermostat(cls, device):
        return device.type == MAX_THERMOSTAT or device.type == MAX_THERMOSTAT_PLUS
