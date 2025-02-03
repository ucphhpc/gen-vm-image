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

import requests
import time


async def download_file(url, output_path, chunk_size=8192):
    response = {}
    try:
        with open(output_path, "wb") as _file:
            response["download_destination"] = output_path
            with requests.get(url, stream=True) as r:
                response["download_src"] = url
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))
                downloaded = 0
                start_time = time.time()
                for chunk in r.iter_content(chunk_size=chunk_size):
                    downloaded += len(chunk)
                    percentage_progress = (downloaded / total) * 100
                    response["download_progress"] = "{:.2f}%".format(
                        percentage_progress
                    )
                    _file.write(chunk)
                stop_time = time.time()
                response["download_time"] = "{:.2f} seconds".format(
                    stop_time - start_time
                )
    except Exception as e:
        response["msg"] = str(e)
        return False, response
    return True, response
