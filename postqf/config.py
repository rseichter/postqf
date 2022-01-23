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
from argparse import Namespace
from datetime import datetime
from re import Pattern


class Cutoff:
    """Representation of a 'cutoff' datetime."""
    always_true: bool
    before: bool
    threshold: datetime

    def __init__(self, before: bool, threshold: datetime, always_true=False) -> None:
        """Initialise object.

        Args:
            before: True signals "before threshold", False means "after threshold".
            threshold: The cutoff threshold.
        """
        super().__init__()
        self.always_true = always_true
        self.before = before
        self.threshold = threshold


class Config:
    """PostQF configuration elements."""
    args: Namespace
    cutoff: Cutoff
    qname_re: Pattern
    rcpt_re: Pattern
    reason_re: Pattern
    sender_re: Pattern


# Shared configuration object
cf = Config()
