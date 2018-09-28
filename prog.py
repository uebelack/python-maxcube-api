import argparse
import sys

from maxcube.connection import MaxCubeConnection
from maxcube.cube import MaxCube


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Set or dump thermostat programmes')
    parser.add_argument('--host', required=True)
    parser.add_argument('--port', required=True, type=int)
    parser.add_argument('cmd', choices=['load', 'dump'])
    args = parser.parse_args()
    cube = MaxCube(MaxCubeConnection(args.host, args.port))
    if args.cmd == 'load':
        cube.set_programmes_from_config(sys.stdin)
    elif args.cmd == 'dump':
        print(cube.devices_as_json())
