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
import re

from postqf.config import Interval
from postqf.config import cf
from postqf.filter import arrival_match
from postqf.filter import rcpt_match
from postqf.filter import reason_match
from postqf.filter import str_match
from postqf.logstuff import level_from_str
from tests import PostqfTestCase


class TestFilter(PostqfTestCase):
    def test_match(self):
        pattern = re.compile('.')
        self.assertTrue(str_match(pattern, 'eggs'))

    def test_mismatch(self):
        pattern = re.compile(r'^ham$')
        self.assertFalse(str_match(pattern, 'eggs'))

    def test_arrival_match(self):
        cf.interval = Interval()
        arrival_match(1)
        self.assertTrue(arrival_match(1))


class TestLog(PostqfTestCase):
    def test_invalid(self):
        with self.assertRaises(ValueError):
            level_from_str('invalid')

    def test_valid(self):
        self.assertEqual(logging.FATAL, level_from_str('FATAL'))


class TestRcpt(PostqfTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.config_re('sender_re', r'@example\.com$')
        self.config_re('rcpt_re', r'@example\.net$')
        self.config_re('reason_re', 'over quota')

    def test_empty(self):
        self.assertFalse(rcpt_match(list()))

    def test_match(self):
        self.assertTrue(rcpt_match(self.recipients()))

    def test_reason_match(self):
        self.assertTrue(reason_match(self.recipients()))

    def test_reason_mismatch(self):
        self.config_re('reason_re', 'gone mad')
        self.assertFalse(reason_match(self.recipients()))

    def test_reason_unavailable(self):
        r = [{'foo': 'bar'}]
        self.config_re('reason_re', '.')
        self.assertTrue(reason_match(r))

    def test_rcpt_mismatch(self):
        self.config_re('rcpt_re', r'@example\.edu')
        self.assertFalse(rcpt_match(self.recipients()))
