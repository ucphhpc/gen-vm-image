# Copyright (C) 2024  The gen-vm-image Project by the Science HPC Center at UCPH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


SUCCESS = 0
PATH_NOT_FOUND_ERROR = 1
PATH_NOT_FOUND_ERROR_MSG = "Path not found: {} - error: {}"
PATH_LOAD_ERROR = 2
PATH_LOAD_ERROR_MSG = "Failed to load path: {}"
PATH_CREATE_ERROR = 3
PATH_CREATE_ERROR_MSG = "Failed to create path: {} - error: {}"
MISSING_ATTRIBUTE_ERROR = 4
MISSING_ATTRIBUTE_ERROR_MSG = "Missing attribute: {} in {}"
INVALID_ATTRIBUTE_TYPE_ERROR = 5
INVALID_ATTRIBUTE_TYPE_ERROR_MSG = (
    "Invalid attribute type: {} for value: {} - must be {}"
)
CHECKSUM_ERROR = 6
RESIZE_ERROR = 7
RESIZE_ERROR_MSG = "Failed to resize path: {}"
CHECK_ERROR = 8
CHECK_ERROR_MSG = "Failed to check path: {}"
JSON_DUMP_ERROR = 9
JSON_DUMP_ERROR_MSG = "Failed to dump JSON: {}"
DOWNLOAD_ERROR = 10
GETSIZE_ERROR = 11
GETSIZE_ERROR_MSG = "Failed to get the size of path {}"
