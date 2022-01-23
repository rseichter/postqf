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
import re

from postqf.filter import str_match
from tests import PostqfTestCase


class Test(PostqfTestCase):
    def test_match(self):
        pattern = re.compile('.')
        self.assertTrue(str_match(pattern, 'eggs'))

    def test_mismatch(self):
        pattern = re.compile(r'^ham$')
        self.assertFalse(str_match(pattern, 'eggs'))
