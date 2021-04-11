import os

from maxcube.cube import MaxCube
from maxcube.device import (
    MAX_DEVICE_MODE_AUTOMATIC,
    MAX_DEVICE_MODE_MANUAL,
    MAX_THERMOSTAT,
    MAX_THERMOSTAT_PLUS,
    MAX_WALL_THERMOSTAT,
    MAX_WINDOW_SHUTTER,
)

cube = MaxCube(os.environ.get("MAXCUBE_IP", "192.168.0.20"), 62910)

print("Serial: %s" % (cube.serial))
for room in cube.rooms:
    print("Room: " + room.name)
    for device in cube.devices_by_room(room):
        print("Device: " + device.name)

print("")

for device in cube.devices:
    if device.type == MAX_THERMOSTAT:
        type = "MAX_THERMOSTAT"
    elif device.type == MAX_THERMOSTAT_PLUS:
        type = "MAX_THERMOSTAT_PLUS"
    elif device.type == MAX_WINDOW_SHUTTER:
        type = "MAX_WINDOW_SHUTTER"
    elif device.type == MAX_WALL_THERMOSTAT:
        type = "MAX_WALL_THERMOSTAT"
    print("Type:   " + type)
    print("RF:     " + device.rf_address)
    print("Room ID:" + str(device.room_id))
    print("Room:   " + cube.room_by_id(device.room_id).name)
    print("Name:   " + device.name)
    print("Serial: " + device.serial)

    if device.type == MAX_THERMOSTAT:
        print("MaxSetP:" + str(device.max_temperature))
        print("MinSetP:" + str(device.min_temperature))
        if device.mode == MAX_DEVICE_MODE_AUTOMATIC:
            mode = "AUTO"
        elif device.mode == MAX_DEVICE_MODE_MANUAL:
            mode = "MANUAL"
        print("Mode:   " + mode)
        print("Actual: " + str(device.actual_temperature))
        print("Target: " + str(device.target_temperature))

    if device.type == MAX_WALL_THERMOSTAT:
        print("MaxSetP:" + str(device.max_temperature))
        print("MinSetP:" + str(device.min_temperature))
        if device.mode == MAX_DEVICE_MODE_AUTOMATIC:
            mode = "AUTO"
        elif device.mode == MAX_DEVICE_MODE_MANUAL:
            mode = "MANUAL"
        print("Mode:   " + mode)
        print("Actual: " + str(device.actual_temperature))
        print("Target: " + str(device.target_temperature))

    if device.type == MAX_WINDOW_SHUTTER:
        print("IsOpen: " + str(device.is_open))

    print("")

for device in cube.devices:
    print(device)
    if device.is_wallthermostat() or device.is_thermostat():
        print("Setting temp")
        cube.set_target_temperature(device, 8)
    else:
        print("No Thermostat")

print("")

for device in cube.devices:
    print(device)
    if device.is_wallthermostat():
        print("Setting mode")
        cube.set_mode(device, MAX_DEVICE_MODE_MANUAL)
    else:
        print("No Wall Thermostat")
