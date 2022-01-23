# Copyright © 2022 Ralph Seichter
#
# This file is part of PostQF.
#
# PostQF is free software: you can redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# PostQF is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with PostQF.
# If not, see <https://www.gnu.org/licenses/>.
import logging

from postqf.logstuff import level_from_str
from tests import PostqfTestCase


class Test(PostqfTestCase):
    def test_invalid(self):
        with self.assertRaises(ValueError):
            level_from_str('invalid')

    def test_valid(self):
        self.assertEqual(logging.FATAL, level_from_str('FATAL'))
