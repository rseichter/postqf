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

from postqf.filter import rcpt_match
from tests import PostqfTestCase


class Test(PostqfTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.config_re('sender_re', r'@example\.com$')
        self.config_re('rcpt_re', r'@example\.net$')
        self.config_re('reason_re', 'over quota')

    def test_empty(self):
        self.assertFalse(rcpt_match(list()))

    def test_match(self):
        self.assertTrue(rcpt_match(self.recipients()))

    def test_reason_mismatch(self):
        self.config_re('reason_re', 'gone mad')
        self.assertFalse(rcpt_match(self.recipients()))

    def test_rcpt_mismatch(self):
        self.config_re('rcpt_re', r'@example\.edu')
        self.assertFalse(rcpt_match(self.recipients()))
