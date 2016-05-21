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

import requests
import json
import errors
import pickle
import sqlite3

"""Generates a simple map with markers using the Google API.

"""
__author__ = "Carl Evans"
__copyright__ = "Copyright 2016 Carl Evans"
__license__ = "Apache 2.0"
__title__ = "Map"
__version__ = "1.0"


class Api(object):
    """Map API class.

    Contains all of the relevant API functions for generating maps and markers.

    Attributes:
        centre_address: An address to centre the map on when starting.
        zoom: The initial zoom level for the centre_address location.
    """
    def __init__(self, centre_address=None, zoom=None):
        if centre_address is None or zoom is None:
            raise errors.Error("[%s.%s] - You must provide an address string to centre the map around, "
                               "and a zoom level for this location." % (__name__, self.__class__.__name__))
        else:
            self.centre_latlng = self.geocode(centre_address)
            self.zoom = zoom
            self._markers = []

    def geocode(self, location):
        """Resolves a latitude and longitude from a location string.

        If the address has been requested before then return the latlng from a GeoCache instance.

        Args:
            location = A string containing a location.

        Returns:
            A tuple containing the latitude and longitude.

        Raises:
            If the location cannot be found it will cause an IndexError exception, which is caught. A custom
            Exception will be raised from this.
        """
        # Instantiate a GeoCache instance and attempt to fetch the location.
        cache = GeoCache()
        cache_result = cache.fetch_location(location)

        if cache_result:
            latlng = cache_result
        else:
            try:
                response = requests.get('http://maps.googleapis.com/maps/api/geocode/json?address="%s"' % location)
                latlng_dict = json.loads(response.text)
                latlng_dict = latlng_dict['results'][0]['geometry']['location']
            except IndexError as e:
                raise errors.Error("[%s.%s] - An error occurred while attempting to geocode location string '%s'. "
                                   "Detail: %s" % (__name__, self.__class__.__name__, location, e))
            else:
                latlng = latlng_dict['lat'], latlng_dict['lng']
                cache.store_location(location, latlng)

        return latlng

    def add_marker(self, marker):
        """Simply adds a populated marker instance to the instance's marker list, ready for map generation.

        Args:
            marker = A populated Marker instance.
        """
        self._markers.append(marker)

    def _decode_markers(self):
        """Iterates through the instance's list of markers, generating javascript markers for the map.

        Returns:
            A string containing javascript markers.
        """
        markers = "\n".join(
            [
              """
               new google.maps.Marker({{
               position: new google.maps.LatLng({lat}, {lng}),
               map: map,
               optimized: false,
               title: "{title}",
               icon: "{icon}"
                }});
              """.format(lat=marker.latlng[0], lng=marker.latlng[1],
                         title=marker.title, icon=marker.image_path) for marker in self._markers
            ])

        return markers

    def generate(self, filename):
        """Generates the html map file using the initial location and zoom level passed during construction.

        Args:
            filename = A filename or path+filename for the generated map html file.
        """
        html = """
                <script src="https://maps.googleapis.com/maps/api/js?v=3.exp&sensor=false"></script>
                <div id="map-canvas" style="height: 100%; width: 100%"></div>
                <script type="text/javascript">
                    var map;
                    function show_map() {{
                        map = new google.maps.Map(document.getElementById("map-canvas"), {{
                            zoom: {zoom},
                            center: new google.maps.LatLng({centre_lat},{centre_lng})
                        }});
                        {markers}
                    }}
                    google.maps.event.addDomListener(window, 'load', show_map);
                </script>
                """.format(centre_lat=self.centre_latlng[0],
                           centre_lng=self.centre_latlng[1],
                           zoom=self.zoom,
                           markers=self._decode_markers())

        with open(filename, "w") as html_file:
            print(html, file=html_file)


class Marker(object):
    """A map marker.

    A simple entity for map markers.

    Attributes:
        latlng: A tuple containing the latitude and longitude for the marker. You can use the geocode method in the
                Api instance to generate these from an address.
        title: A string containing the marker's title. This will be shown in the marker's tooltip.
        image_path: A string containing the path to the marker image.
    """
    def __init__(self, latlng=None, title=None, image_path=None):
        if latlng is None or title is None or image_path is None:
            raise errors.Error("[%s.%s] - You must provide a marker latlng, a title and an image path."
                               % (__name__, self.__class__.__name__))
        else:
            self.latlng = latlng
            self.title = title
            self.image_path = image_path


class GeoCache(object):
    """GeoCache class.

    Retrieves or stores location data in a sqlite database cache.

    Attributes:
        db_name: An optional database name. Defaults to 'geocache.db'.
    """
    def __init__(self, db_name="geocache.db"):
        self.connection = sqlite3.connect(db_name)

        # Create the table if it doesn't already exist.
        cursor = self.connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS GeoCache (location STRING PRIMARY KEY, latlng BLOB)")
        self.connection.commit()

    def fetch_location(self, location):
        """Attempts to find the passed location string in the cache.

        Args:
            location = A string containing a location to be retrieved.

        Returns:
            A latlng tuple if the location is found, or a boolean False if not.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT latlng FROM GeoCache WHERE location='%s'" % location)
        latlng = cursor.fetchone()

        if latlng is None:
            return False
        else:
            return pickle.loads(latlng[0])

    def store_location(self, location, latlng):
        """Stores a latlng against a location in the cache.

        Args:
            location = A string containing a location to be stored.
            latlng = A latlng tuple to be stored against a location string.
        """
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO GeoCache(location, latlng) VALUES(?, ?)",
                       (location, sqlite3.Binary(pickle.dumps(latlng, -1))))
        self.connection.commit()
