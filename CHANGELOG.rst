### Version 0.4.0
 * Issues fixed:
   - [MaxCube reset to fatory defaults](https://github.com/hackercowboy/python-maxcube-api/issues/12)
   - [Unable to change back to scheduled temperature (auto mode)](https://github.com/hackercowboy/python-maxcube-api/issues/24

 * Breaking changes:
   - Increased minimum supported version of Python to >= 3.7
   - MaxCubeConnection object removed. MaxCube constructor now receives
     the host and port parameters directly
   - The connection is not released after each command is send. This
     can block other applications to connect to the Max! Cube. You
     can call cube disconnect() method to release the connection
     manually.
