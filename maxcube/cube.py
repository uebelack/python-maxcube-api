import json
import base64
import struct

from .commander import Commander
from maxcube.device import \
    MaxDevice, \
    MAX_CUBE, \
    MAX_THERMOSTAT, \
    MAX_THERMOSTAT_PLUS, \
    MAX_WINDOW_SHUTTER, \
    MAX_WALL_THERMOSTAT, \
    MAX_DEVICE_MODE_AUTOMATIC, \
    MAX_DEVICE_MODE_MANUAL, \
    MAX_DEVICE_BATTERY_OK, \
    MAX_DEVICE_BATTERY_LOW
from maxcube.room import MaxRoom
from maxcube.thermostat import MaxThermostat
from maxcube.wallthermostat import MaxWallThermostat
from maxcube.windowshutter import MaxWindowShutter
import logging

logger = logging.getLogger(__name__)

CMD_SET_PROG = "10"
UNKNOWN = "00"
RF_FLAG_IS_ROOM = "04"
RF_FLAG_IS_DEVICE = "00"
RF_NULL_ADDRESS = "000000"
DAYS = ['saturday', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday',
        'friday', 'saturday', 'sunday']


class MaxCube(MaxDevice):
    def __init__(self, host: str, port: int):
        super(MaxCube, self).__init__()
        self.__commander = Commander(host, port)
        self.name = 'Cube'
        self.type = MAX_CUBE
        self.firmware_version = None
        self.devices = []
        self.rooms = []
        self.update()
        self.log()

    def disconnect(self):
        self.__commander.disconnect()

    def log(self):
        logger.info('Cube (rf=%s, firmware=%s)' % (self.rf_address, self.firmware_version))
        for device in self.devices:
            if device.is_thermostat():
                logger.info('Thermostat (type=%s, rf=%s, room=%s, name=%s, mode=%s, min=%s, max=%s, actual=%s, target=%s, valve=%s)'
                            % (device.type, device.rf_address, self.room_by_id(device.room_id).name, device.name,
                               device.mode, device.min_temperature, device.max_temperature,
                               device.actual_temperature, device.target_temperature, device.valve_position))
            elif device.is_wallthermostat():
                logger.info('WallThermostat (type=%s, rf=%s, room=%s, name=%s, min=%s, max=%s, actual=%s, target=%s)'
                            % (device.type, device.rf_address, self.room_by_id(device.room_id).name, device.name,
                               device.min_temperature, device.max_temperature,
                               device.actual_temperature, device.target_temperature))
            elif device.is_windowshutter():
                logger.info('WindowShutter (type=%s, rf=%s, room=%s, name=%s, init=%s, open=%s)'
                            % (device.type, device.rf_address, self.room_by_id(device.room_id).name, device.name,
                               device.initialized, device.is_open))
            else:
                logger.info('Device (rf=%s, name=%s' % (device.rf_address, device.name))

    def update(self):
        self.__parse_responses(self.__commander.update())

    def get_devices(self):
        return self.devices

    def device_by_rf(self, rf):
        for device in self.devices:
            if device.rf_address == rf:
                return device
        return None

    def devices_by_room(self, room):
        rooms = []

        for device in self.devices:
            if device.room_id == room.id:
                rooms.append(device)

        return rooms

    def get_rooms(self):
        return self.rooms

    def room_by_id(self, id):
        for room in self.rooms:
            if room.id == id:
                return room
        return None

    def __parse_responses(self, messages):
        for msg in messages:
            cmd = msg.cmd
            if cmd == 'C':
                self.parse_c_message(msg.arg)
            elif cmd == 'H':
                self.parse_h_message(msg.arg)
            elif cmd == 'L':
                self.parse_l_message(msg.arg)
            elif cmd == 'M':
                self.parse_m_message(msg.arg)
            else:
                logger.debug('Ignored unsupported message: %s' % (msg))

    def parse_c_message(self, message):
        logger.debug('Parsing c_message: ' + message)
        params = message.split(',')
        device_rf_address = params[0].upper()
        data = bytearray(base64.b64decode(params[1]))

        length = data[0]
        rf_address = self.parse_rf_address(data[1: 3])
        device_type = data[4]

        device = self.device_by_rf(device_rf_address)

        if device and device.is_thermostat():
            device.comfort_temperature = data[18] / 2.0
            device.eco_temperature = data[19] / 2.0
            device.max_temperature = data[20] / 2.0
            device.min_temperature = data[21] / 2.0
            device.programme = get_programme(data[29:])

        if device and device.is_wallthermostat():
            device.comfort_temperature = data[18] / 2.0
            device.eco_temperature = data[19] / 2.0
            device.max_temperature = data[20] / 2.0
            device.min_temperature = data[21] / 2.0

        if device and device.is_windowshutter():
            # Pure Speculation based on this:
            # Before: [17][12][162][178][4][0][20][15]KEQ0839778
            # After:  [17][12][162][178][4][1][20][15]KEQ0839778
            device.initialized = data[5]

    def parse_h_message(self, message):
        logger.debug('Parsing h_message: ' + message)
        tokens = message.split(',')
        self.rf_address = tokens[1]
        self.firmware_version = (tokens[2][0:2]) + '.' + (tokens[2][2:4])

    def parse_m_message(self, message):
        logger.debug('Parsing m_message: ' + message)
        data = bytearray(base64.b64decode(message.split(',')[2]))
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

            room = self.room_by_id(room_id)

            if not room:
                room = MaxRoom()
                room.id = room_id
                room.name = name
                self.rooms.append(room)
            else:
                room.name = name

        num_devices = data[pos]
        pos += 1

        for device_idx in range(0, num_devices):
            device_type = data[pos]
            device_rf_address = self.parse_rf_address(data[pos + 1: pos + 1 + 3])
            device_serial = data[pos + 4: pos + 14].decode('utf-8')
            device_name_length = data[pos + 14]
            device_name = data[pos + 15: pos + 15 + device_name_length].decode('utf-8')
            room_id = data[pos + 15 + device_name_length]

            device = self.device_by_rf(device_rf_address)

            if not device:
                if device_type == MAX_THERMOSTAT or device_type == MAX_THERMOSTAT_PLUS:
                    device = MaxThermostat()

                if device_type == MAX_WINDOW_SHUTTER:
                    device = MaxWindowShutter()

                if device_type == MAX_WALL_THERMOSTAT:
                    device = MaxWallThermostat()

                if device:
                    self.devices.append(device)

            if device:
                device.type = device_type
                device.rf_address = device_rf_address
                device.room_id = room_id
                device.name = device_name
                device.serial = device_serial

            pos += 1 + 3 + 10 + device_name_length + 2

    def parse_l_message(self, message):
        logger.debug('Parsing l_message: ' + message)
        data = bytearray(base64.b64decode(message))
        pos = 0

        while pos < len(data):
            length = data[pos]
            device_rf_address = self.parse_rf_address(data[pos + 1: pos + 4])
            flags = data[pos + 5: pos + 6]

            device = self.device_by_rf(device_rf_address)

            if device:
                bits1, bits2 = struct.unpack('BB', bytearray(data[pos + 5: pos + 7]))
                device.battery = self.resolve_device_battery(bits2)

            # Thermostat or Wall Thermostat
            if device and (device.is_thermostat() or device.is_wallthermostat()):
                device.target_temperature = (data[pos + 8] & 0x7F) / 2.0
                bits1, bits2 = struct.unpack('BB', bytearray(data[pos + 5: pos + 7]))
                device.mode = self.resolve_device_mode(bits2)

            # Thermostat
            if device and device.is_thermostat():
                device.valve_position = data[pos + 7]
                if device.mode == MAX_DEVICE_MODE_MANUAL or device.mode == MAX_DEVICE_MODE_AUTOMATIC:
                    actual_temperature = ((data[pos + 9] & 0xFF) * 256 + (data[pos + 10] & 0xFF)) / 10.0
                    if actual_temperature != 0:
                        device.actual_temperature = actual_temperature
                else:
                    device.actual_temperature = None

            # Wall Thermostat
            if device and device.is_wallthermostat():
                device.actual_temperature = (((data[pos + 8] & 0x80) << 1) + data[pos + 12]) / 10.0

            # Window Shutter
            if device and device.is_windowshutter():
                status = data[pos + 6] & 0x03
                if status > 0:
                    device.is_open = True
                else:
                    device.is_open = False

            # Advance our pointer to the next submessage
            pos += length + 1

    def set_target_temperature(self, thermostat, temperature):
        return self.set_temperature_mode(thermostat, temperature, None)

    def set_mode(self, thermostat, mode):
        return self.set_temperature_mode(thermostat, None, mode)

    def set_temperature_mode(self, thermostat, temperature, mode):
        logger.debug('Setting temperature %s and mode %s on %s!', temperature, mode, thermostat.rf_address)

        if not thermostat.is_thermostat() and not thermostat.is_wallthermostat():
            logger.error('%s is no (wall-)thermostat!', thermostat.rf_address)
            return

        if mode is None:
            mode = thermostat.mode
        if temperature is None:
            temperature = 0 if mode == MAX_DEVICE_MODE_AUTOMATIC else thermostat.target_temperature

        rf_address = thermostat.rf_address
        room = to_hex(thermostat.room_id)
        target_temperature = int(temperature * 2) + (mode << 6)

        byte_cmd = '000440000000' + rf_address + room + to_hex(target_temperature)
        if self.__commander.send_radio_msg(byte_cmd):
            thermostat.mode = mode
            if temperature > 0:
                thermostat.target_temperature = int(temperature * 2) / 2.0
            return True
        return False

    def set_programme(self, thermostat, day, metadata):
        # compare with current programme
        if thermostat.programme[day] == metadata:
            logger.debug("Skipping setting unchanged programme for " + day)
            return

        heat_time_tuples = [(x["temp"], x["until"]) for x in metadata]
        # pad heat_time_tuples so that there are always seven
        for _ in range(7 - len(heat_time_tuples)):
            heat_time_tuples.append((0, "00:00"))
        command = ""
        if thermostat.is_room():
            rf_flag = RF_FLAG_IS_ROOM
            devices = self.devices_by_room(thermostat)
        else:
            rf_flag = RF_FLAG_IS_DEVICE
            devices = [thermostat]
        command += UNKNOWN + rf_flag + CMD_SET_PROG + RF_NULL_ADDRESS
        for device in devices:
            command += device.rf_address
            command += to_hex(device.room_id)
            command += to_hex(n_from_day_of_week(day))
            for heat, time in heat_time_tuples:
                command += temp_and_time(heat, time)
        return self.__commander.send_radio_msg(command)

    def devices_as_json(self):
        devices = []
        for device in self.devices:
            devices.append(device.to_dict())
        return json.dumps(devices, indent=2)

    def set_programmes_from_config(self, config_file):
        config = json.load(config_file)
        for device_config in config:
            device = self.device_by_rf(device_config['rf_address'])
            programme = device_config['programme']
            if not programme:
                # e.g. a wall thermostat
                continue
            for day, metadata in programme.items():
                self.set_programme(device, day, metadata)

    @classmethod
    def resolve_device_mode(cls, bits):
        return (bits & 3)

    @classmethod
    def resolve_device_battery(cls, bits):
        return (bits >> 7)

    @classmethod
    def parse_rf_address(cls, address):
        return ''.join('{:02X}'.format(x) for x in address)


def get_programme(bits):
    n = 26
    programme = {}
    days = [bits[i:i + n] for i in range(0, len(bits), n)]
    for j, day in enumerate(days):
        n = 2
        settings = [day[i:i + n] for i in range(0, len(day), n)]
        day_programme = []
        for setting in settings:
            word = format(setting[0], "08b") + format(setting[1], "08b")
            temp = int(int(word[:7], 2) / 2)
            time_mins = int(word[7:], 2) * 5
            mins = time_mins % 60
            hours = int((time_mins - mins) / 60)
            time = "{:02d}:{:02d}".format(hours, mins)
            day_programme.append({"temp": temp, "until": time})
            if time == "24:00":
                # This appears to flag the end of useable set points
                break
        programme[day_of_week_from_n(j)] = day_programme
    return programme


def n_from_day_of_week(day):
    return DAYS.index(day)


def day_of_week_from_n(day):
    return DAYS[day]


def temp_and_time(temp, time):
    temp = float(temp)
    assert temp <= 32, "Temp must be 32 or lower"
    assert temp % 0.5 == 0, "Temp must be increments of 0.5"
    temp = int(temp * 2)
    hours, mins = [int(x) for x in time.split(":")]
    assert mins % 5 == 0, "Time must be a multiple of 5 mins"
    mins = hours * 60 + mins
    bits = format(temp, "07b") + format(int(mins/5), "09b")
    return to_hex(int(bits, 2))


def to_hex(value):
    "Return value as hex word"
    return format(value, "02X")
