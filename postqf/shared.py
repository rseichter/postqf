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
import datetime
from argparse import Namespace
from re import Pattern


class Cutoff:
    before: bool
    threshold: datetime.datetime

    def __init__(self, before, threshold) -> None:
        super().__init__()
        self.before = before
        self.threshold = threshold


class Config:
    args: Namespace
    cutoff: Cutoff
    qname_re: Pattern
    rcpt_re: Pattern
    reason_re: Pattern
    sender_re: Pattern


cf = Config()
