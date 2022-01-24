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
from datetime import datetime
from datetime import timedelta
from unittest import TestCase

from postqf.config import Interval

now_dt = datetime.now()
now_epoch = int(now_dt.timestamp())
delta = timedelta(seconds=10)


def _epoch(d: datetime) -> int:
    return int(d.timestamp())


def _past(reference: datetime, delta: timedelta):
    return reference - delta


class TestInterval(TestCase):
    def test_default_interval(self):
        t = _past(datetime.now(), timedelta(seconds=1))
        self.assertTrue(Interval().wraps(t))

    def test_both_boundaries(self):
        t = _past(datetime.now(), timedelta(minutes=1))
        self.assertTrue(Interval(after='2022-01-24', before='30s').wraps(t))

    def test_lower_hr(self):
        self.assertTrue(Interval(after='1s').wraps(datetime.now()))

    def test_lower_iso(self):
        self.assertTrue(Interval(after='2022-01-24').wraps(datetime.now()))

    def test_upper_hr(self):
        t = _past(datetime.now(), timedelta(seconds=2))
        self.assertTrue(Interval(before='1s').wraps(t))

    def test_upper_iso(self):
        t = datetime.fromisoformat('2022-01-23')
        self.assertTrue(Interval(before='2022-01-24').wraps(t))
