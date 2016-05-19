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

    def geocode(self, location_string):
        """Fetches a latitude and longitude dictionary from a location string.

        Returns:
            A dictionary containing the latitude and longitude.

        Raises:
            If the location cannot be found it will cause an IndexError exception, which is caught. A custom
            Exception will be raised from this.
        """
        try:
            latlng = requests.get('http://maps.googleapis.com/maps/api/geocode/json?address="%s"' % location_string)
            latlng = json.loads(latlng.text)
            latlng_dict = latlng['results'][0]['geometry']['location']
        except IndexError as e:
            raise errors.Error("[%s.%s] - An error occurred while attempting to geocode location string '%s'. "
                               "Detail: %s" % (__name__, self.__class__.__name__, location_string, e))
        else:
            return latlng_dict['lat'], latlng_dict['lng']

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
