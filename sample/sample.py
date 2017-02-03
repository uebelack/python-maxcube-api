from maxcube.cube import MaxCube
from maxcube.connection import MaxCubeConnection

cube = MaxCube(MaxCubeConnection('192.168.0.20', 62910))

for device in cube.devices:
    print(device.name)
    print(device.actual_temperature)
    print(device.target_temperature)

    cube.set_target_temperature(device, 18)

