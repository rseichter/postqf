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

from postqf import config
from postqf.config import Cutoff
from postqf.filter import arrival_match
from tests import PostqfTestCase

now_dt = datetime.utcnow()
now_epoch = int(now_dt.timestamp())
delta = timedelta(seconds=10)


class Test(PostqfTestCase):
    def test_always_true(self):
        config.cf.cutoff = Cutoff(before=True, threshold=now_dt, always_true=True)
        self.assertTrue(arrival_match(-1))

    def test_after(self):
        past = now_dt - delta
        config.cf.cutoff = Cutoff(before=False, threshold=past)
        self.assertTrue(arrival_match(now_epoch))

    def test_before(self):
        past = int((now_dt - delta).timestamp())
        config.cf.cutoff = Cutoff(before=True, threshold=now_dt)
        self.assertTrue(arrival_match(past))
