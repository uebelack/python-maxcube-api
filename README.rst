eQ-3/ELV MAX! Cube Python API |Build Status| |Coverage Status|
===============================================================

A python api to control the Max! Cube thermostats:

- get basic info about the cube itself
- get info about the max thermostats connected to the cube (mode, temperatures ...)

Basic usage:

.. code:: python

    from maxcube.cube import MaxCube

    cube = MaxCube('192.168.0.20')

    for device in cube.devices:
        print(device.name)
        print(device.actual_temperature)

This api was build for the integration of the Max! thermostats into `Home Assistant <https://home-assistant.io>`__ and
mostly only covers the functions needed for the integration.

It does also include functions needed to save and restore thermostat programmes.  For example:


.. code:: shell

    # dump programmes (and other data) to a JSON file
    python3 prog.py dump --host=192.168.0.11 > backup.json

    # load programmes (not other data!) from a JSON file
    python3 prog.py load --host=192.168.0.11 < backup.json


Running tests
=============

.. code:: python

   python3 -m unittest discover tests/

Acknowledgements
================

Thanks to:

-  `https://github.com/Bouni/max-cube-protocol <https://github.com/Bouni/max-cube-protocol>`__
-  `https://github.com/ercpe/pymax <https://github.com/ercpe/pymax>`__
-  `https://github.com/aleszoulek/maxcube <https://github.com/aleszoulek/maxcube>`__
-  `openhab integration <https://github.com/openhab/openhab2/tree/master/addons/binding/org.openhab.binding.max>`__

.. |Build Status| image:: https://travis-ci.org/hackercowboy/python-maxcube-api.svg?branch=master
   :target: https://travis-ci.org/hackercowboy/python-maxcube-api
.. |Coverage Status| image:: https://coveralls.io/repos/hackercowboy/python-maxcube-api/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/hackercowboy/python-maxcube-api?branch=master
