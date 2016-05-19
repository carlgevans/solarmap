#!/usr/bin/env python3
#
# Copyright 2016 Carl Evans
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import solarwinds
import map
import errors
import logging
import configparser
import os

"""Generates a Google Map with SolarWinds node locations as points.

"""
__author__ = "Carl Evans"
__copyright__ = "Copyright 2016 Carl Evans"
__license__ = "Apache 2.0"
__title__ = "SolarMap"
__version__ = "1.0"


class SolarMap(object):
    """SolarMap class.

    Attributes:
        sw_api: A SolarWinds API instance.
        map_api: A Map instance.
        sw_location: The field in SolarWinds that contains the location data.
        logger: A logging instance from the Python logging library.
    """
    def __init__(self, sw_api=None, map_api=None, sw_location=None, logger=None):
        if sw_api is None or map_api is None or sw_location is None or logger is None:
            raise errors.Error("[%s.%s] - You must provide a SolarWinds API instance, a Map instance, "
                               "a logger instance and the SolarWinds location field."
                               % (__name__, self.__class__.__name__))
        else:
            self.sw_api = sw_api
            self.map_api = map_api
            self.sw_location = sw_location
            self.logger = logger

    def get_node_locations(self):
        """Get a list of distinct node locations and their highest statuses.

        Returns:
            A list of tuples containing the location and highest status value.
        """
        locations = self.sw_api.query("SELECT DISTINCT Nodes.CustomProperties.%s as Location, "
                                      "MAX(Nodes.Status) as Status "
                                      "FROM Orion.Nodes "
                                      "GROUP BY Nodes.CustomProperties.%s"
                                      % (self.sw_location, self.sw_location))

        location_list = []

        for location in locations['results']:
            location_list.append((location['Location'], location['Status']))

        return location_list

    def parse_locations(self, location_list):
        """Perform any custom parsing of the location field contents here and then pass a list of tuples back.

         Returns:
            A list of tuples containing the parsed locations and highest status value.
         """
        parsed_locations = location_list

        return parsed_locations

    def generate(self):
        """Populates the list of markers in the map instance before calling the generate method to create
        the map html file.

        """
        location_list = self.get_node_locations()
        location_list = self.parse_locations(location_list)

        for location in location_list:
            try:
                latlng = self.map_api.geocode(location[0])
            except errors.Error as error:
                self.logger.error("[%s.%s] - Location string '%s' not found by geocoding. Detail: %s"
                                  % (__name__, self.__class__.__name__, location[0], error))

            else:
                if location[1] == 1 or location[1] == 9:
                    new_marker = map.Marker(latlng, location[0], "markers/green.png")
                else:
                    new_marker = map.Marker(latlng, location[0], "markers/red.png")

                self.map_api.add_marker(new_marker)

        self.map_api.generate("map.html")


def main():
    # Read settings file.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "settings.ini")
    config = configparser.ConfigParser()
    config.read(config_path)
    settings = config['Settings']

    # Configure logging.
    logging.basicConfig(level=logging.DEBUG,
                        filename=settings['log_file'], filemode=settings['log_mode'],
                        format='%(asctime)s %(levelname)s %(message)s')

    try:
        sw_api = solarwinds.Api(settings['sw_api'], settings['sw_username'], settings['sw_password'])
        map_api = map.Api(settings['map_start_location'],settings['map_start_zoom'])

        # Pass the above APIs to the constructor of SolarMap.
        solarmap = SolarMap(sw_api, map_api, settings['sw_location_field'], logging)
    except errors.Error as error:
        logging.error(error)
    else:
        try:
            # Generate Map.
            solarmap.generate()
        except errors.Error as error:
            logging.error(error)


# Only execute the main script if passed to an interpreter. Do not execute if imported.
if __name__ == "__main__":
    main()
