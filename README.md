websdr-config
=============

Configuration and setup files for the WebSDR (note the websdr binaries must NOT be kept in this)

Websdr URL: http://websdr.suws.org.uk/

Documentation URL: http://www.suws.org.uk/wp/suws-websdr/

## WebSDR Config Files

### WebSDR Daemon Configuration File

* cfg/websdr.cfg

### WebSDR Waterfall Marker Flags

* cfg/stationinfo.txt

### WebSDR Main Web Page

* pub/index.html
* dist11/pub2/websdr-controls.html

## Upstart System Service Config Files

* websdr.conf
* rtltcp_dc.conf
* rtltcp_144.conf
* rtltcp_146.conf
* rtltcp_432.conf
* rtltcp_435.conf
* rtltcp_437.conf
* rtltcp_10ghz.conf

## Dependencies

libfftw3-3, libpng12-0

## License

All original and un-attributed work in this repository is licensed as:

Creative Commons Attribution NonCommercial ShareAlike http://creativecommons.org/licenses/by-nc-sa/4.0/

Copyright(C) 2014 Phil Crump <phil@philcrump.co.uk>
