# Copyright (C) 2025  The gen-vm-image Project by the Science HPC Center at UCPH
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

import unittest
import random
from gen_vm_image.common.codes import SUCCESS
from gen_vm_image.common.defaults import SINGLE
from gen_vm_image.cli.cli import main


class TestCLISingleImage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.seed = str(random.random())[2:10]

    def test_cli_help(self):
        return_code = None
        try:
            return_code = main([SINGLE, "--help"])
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)

    def test_cli_basic_single_image(self):
        return_code = None
        try:
            name = "test-cli-single-image-{}".format(self.seed)
            size = "5G"
            return_code = main([SINGLE, name, size])
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)
