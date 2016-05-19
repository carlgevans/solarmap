SolarMaps
==========

Generates a map with markers for the location and statuses of SolarWinds node locations.

© 2016 Carl G. Evans.

https://github.com/carlgevans/solarmaps/

Written in Python.

##1. What is SolarMaps?

SolarMaps communicates with the SolarWinds API to gather a list of distinct locations and their worst status codes.
These location and statuses are then plotted on a map using the Google Maps JavaScript API v3.

This map can then be used as part of a general dashboard or used within SolarWinds by utilising an Iframe.

##2. Libraries

Libraries are not included in the repository, so be sure to install them with command:

pip install -r requirements.txt

* Requests - HTTP requests library.
* ConfigParser - Config file library for reading settings.ini file.

##3. Installation

* Download the source.
* Download the library dependencies with pip (see above).
* Configure the settings (username, password etc) for SolarWinds and set the default map location/zoom level.
* Configure the script to run on a schedule.

##4. Notes

* The requests library uses TLSv1.2 by default. In some cases the SolarWinds server might not support TLSv1.2 and this
  will be displayed in the event viewer as an SChannel error. See the following URL for details.

  http://stackoverflow.com/questions/14102416/python-requests-requests-exceptions-sslerror-errno-8-ssl-c504-eof-occurred

  The HTTPAdapter override solution was not working, but the nasty hack of connectionpool.py did.

* Perform any parsing of your location field in the parse_locations method.

* You can change the custom location field that is queried in the settings file.

##5. License

SolarMaps has been released under the Apache 2.0 license. All contributors agree to transfer ownership of their
code to Carl G. Evans for release under this license.

###5.1 The Apache License

Copyright (c) 2016 Carl G. Evans

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
