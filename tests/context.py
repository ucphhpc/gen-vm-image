# Copyright (C) 2024  rasmunk
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

from gen_vm_image.utils.io import join, remove, exists, makedirs
from gen_vm_image.architecture import load_architecture


class AsyncImageTestContext:
    def __init__(self):
        self.init_done = False

    async def setUp(self):
        if self.init_done:
            return

        # https://cloud.debian.org/images/cloud/bookworm/latest/input_path_image-genericcloud-amd64.qcow2
        # Download the test image for the path input test
        self.test_tmp_directory = join("tests", "tmp")
        self.test_res_directory = join("tests", "res")
        if not exists(self.test_tmp_directory):
            assert makedirs(self.test_tmp_directory)
        self.input_image_path = join(self.test_res_directory, "test.qcow2")
        assert exists(self.input_image_path)

        self.architecture_path = join(
            self.test_res_directory, "advanced_architecture.yml"
        )
        loaded, response = load_architecture(self.architecture_path)
        assert loaded
        assert "architecture" in response

        self.architecture = response["architecture"]
        assert self.architecture is not None
        assert isinstance(self.architecture, dict)

    # Should be used by the non async function tearDownClass to ensure that
    # the following cleanup is done before the class is destroyed
    def tearDown(self):
        assert remove(self.test_tmp_directory, recursive=True)
