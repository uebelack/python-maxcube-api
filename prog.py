import argparse

from maxcube.connection import MaxCubeConnection
from maxcube.cube import MaxCube


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Set or dump thermostat programmes')
    parser.add_argument('cmd', choices=['load', 'dump'])
    parser.add_argument('filename')
    args = parser.parse_args()
    cube = MaxCube(MaxCubeConnection('192.168.1.111', 62910))
    if args.cmd == 'load':
        cube.set_programmes_from_config(args.filename)
    elif args.cmd == 'dump':
        with open(args.filename, "w") as f:
            f.write(cube.devices_as_json())
