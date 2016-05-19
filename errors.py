#!/usr/bin/env python
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

"""Error handling.

A custom error handling class.
"""
__author__ = "Carl Evans"
__copyright__ = "Copyright 2016 Carl Evans"
__license__ = "Apache 2.0"
__title__ = "Errors"
__version__ = "1.0"

class Error(Exception):
    """Custom exception class derived from base Exception class.

    Attributes:
        error_text: A string containing a description of the error.
    """
    def __init__(self, error_text):
        self.error_text = error_text

    def __str__(self):
        return self.error_text