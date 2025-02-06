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

import os
import shutil
import re

from gen_vm_image.common.defaults import DEFAULT_BUFFER_SIZE


def makedirs(path):
    try:
        os.makedirs(os.path.expanduser(path))
        return True
    except Exception:
        # TODO, add logging
        return False
    return False


def load(path, mode="r", readlines=False, handler=None, **load_kwargs):
    try:
        with open(path, mode) as fh:
            if handler:
                return handler.load(fh, **load_kwargs)
            if readlines:
                return fh.readlines()
            return fh.read()
    except Exception:
        # TODO, add logging
        return False
    return False


def write(path, content, mode="w", mkdirs=False, handler=None, **handler_kwargs):
    dir_path = os.path.dirname(path)
    if not os.path.exists(dir_path) and mkdirs:
        if not makedirs(dir_path):
            return False
    try:
        with open(path, mode) as fh:
            if handler:
                handler.dump(content, fh, **handler_kwargs)
            else:
                if isinstance(content, (list, set)):
                    for line in content:
                        fh.write(line)
                else:
                    fh.write(content)
        return True
    except Exception:
        # TODO, add logging
        return False
    return False


def remove(path, recursive=False):
    try:
        if recursive:
            shutil.rmtree(path)
        else:
            os.remove(path)
        return True
    except Exception:
        # TODO, add logging
        return False
    return False


def exists(path):
    return os.path.exists(os.path.expanduser(path))


def join(path, *paths):
    return os.path.join(path, *paths)


def which(command):
    return shutil.which(command)


def chmod(path, mode, **kwargs):
    try:
        os.chmod(os.path.expanduser(path), mode, **kwargs)
        return True
    except Exception:
        # TODO, add logging
        return False
    return False


def chown(path, uid, gid):
    try:
        os.chown(os.path.expanduser(path), uid, gid)
        return True
    except Exception:
        # TODO, add logging
        return False
    return False


def copy(original, target):
    # Copy path to target
    try:
        shutil.copyfile(original, target)
        return True
    except Exception:
        return False
    return False


# Read chunks of a file, default to 64KB
async def hashsum(
    path, algorithm="sha1", buffer_size=DEFAULT_BUFFER_SIZE, read_bytes_of_file=None
):
    try:
        import hashlib

        hash_algorithm = hashlib.new(algorithm)
        if read_bytes_of_file:
            bytes_read = 0
            if buffer_size > read_bytes_of_file:
                buffer_size = read_bytes_of_file

        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(buffer_size), b""):
                hash_algorithm.update(chunk)
                if read_bytes_of_file:
                    bytes_read += buffer_size
                    if (bytes_read + buffer_size) >= read_bytes_of_file:
                        buffer_size = read_bytes_of_file - bytes_read
                    if buffer_size == 0:
                        break

        return hash_algorithm.hexdigest()
    except Exception:
        # TODO, add logging
        return False
    return False


def find(directory_path, regex_name):
    found = []
    for root, dirs, files in os.walk(directory_path):
        for f in files:
            if re.match(regex_name, f):
                found.append(f)
    return found


def size(path):
    """Returns the size of a file in bytes"""
    try:
        return os.path.getsize(path)
    except Exception:
        # TODO, add logging
        return False
    return False
