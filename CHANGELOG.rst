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

### Version 0.4.1
 * Several minor changes:
   - Allow to rollback to non-persistent connections to keep using original software for unsupported operations
   - Serial number of the cube was not extracted from handshake
   - When changing to auto mode, use weekly programme to fetch current temperature
   - Make MAX! Cube TCP port optional

### Version 0.4.2
 * Bug fixes:
   - Interpret correctly S command error responses (https://github.com/home-assistant/core/issues/49075)
   - Support application timezone configuration (https://github.com/home-assistant/core/issues/49076)
 * Improvements in device logging
 * Build improvements:
   * Move from Travis to Github Actions to execute validation actions
   * Add code style and quality checks to the validation actions
