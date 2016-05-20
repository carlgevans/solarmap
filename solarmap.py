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
        map_api: A Map API instance.
        sw_location: The field in SolarWinds that contains the location data.
    """
    def __init__(self, sw_api=None, map_api=None, sw_location=None):
        if sw_api is None or map_api is None or sw_location is None:
            raise errors.Error("[%s.%s] - You must provide a SolarWinds API instance, a Map API instance "
                               "and the SolarWinds location field." % (__name__, self.__class__.__name__))
        else:
            self.sw_api = sw_api
            self.map_api = map_api
            self.sw_location = sw_location

    def get_node_locations(self):
        """Get a list of distinct node locations and their highest statuses.

        Returns:
            A list of Location instances.
        """
        locations = self.sw_api.query("SELECT DISTINCT Nodes.CustomProperties.%s as Location, "
                                      "MAX(Nodes.Status) as Status "
                                      "FROM Orion.Nodes "
                                      "GROUP BY Nodes.CustomProperties.%s"
                                      % (self.sw_location, self.sw_location))

        location_list = []

        for location in locations['results']:
            new_location = Location(location['Location'], location['Status'], self.map_api)
            location_list.append(new_location)

        return location_list

    def plot_locations(self, location_list):
        """Plots the locations on the map from a list of location instances.

        Args:
            location_list = A list of location instances.
        """
        for location in location_list:
            try:
                new_marker = map.Marker(location.latlng, location.address, location.image_path)
            except errors.Error as error:
                logging.error("[%s.%s] - An error occurred while plotting location '%s'. Detail: %s"
                              % (__name__, self.__class__.__name__, location.address, error))
            else:
                self.map_api.add_marker(new_marker)

    def generate(self):
        """Populates a list of locations in the map instance before calling the generate method to create
        the map html file.

        """
        location_list = self.get_node_locations()
        self.plot_locations(location_list)
        self.map_api.generate("map.html")


class Location(object):
    """A SolarMap Location.

    An entity representing a SolarMap location.

    Attributes:
        address: An unparsed string containing location address data.
        status: The location's status. 0 = Unknown, 1 = Up, 2 = Down, 3 = Warning etc.
    """
    def __init__(self, address=None, status=None, map_api=None):
        if address is None or status is None or map_api is None:
            raise errors.Error("[%s.%s] - You must provide an address, a status and a map api instance."
                               % (__name__, self.__class__.__name__))
        else:
            self.address = address
            self.status = status
            self.map_api = map_api

    @property
    def latlng(self):
        """Geocode the parsed address.

         Returns:
            The location's latlng returned as a tuple.
        """
        try:
            latlng = self.map_api.geocode(self.parsed_address)
        except errors.Error as error:
            raise errors.Error("[%s.%s] - LatLng not found for address '%s'. Detail: %s"
                          % (__name__, self.__class__.__name__, self.parsed_address, error))
        else:
            return latlng

    @property
    def parsed_address(self):
        """Perform any custom parsing of the location address attribute here.

         Returns:
            A parsed string containing location address data.
        """
        parsed_address = self.address

        return parsed_address

    @property
    def image_path(self):
        """Determine the correct image to use based upon the status and return the correct image path.

         Returns:
            A string containing the path to the marker image for this location.
        """
        if self.status == 1 or self.status == 9:
            image_path = "markers/green.png"
        else:
            image_path = "markers/red.png"

        return image_path


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
        solarmap = SolarMap(sw_api, map_api, settings['sw_location_field'])
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
