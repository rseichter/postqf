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
from argparse import Namespace
from datetime import datetime
from datetime import timedelta
from re import IGNORECASE
from re import compile


class Interval:
    """Representation of a time interval between two epoch times."""
    DEFAULT_AFTER = '1970-01-01'
    DEFAULT_BEFORE = '9999-12-31'
    unit_seconds_map = {
        's': 1,
        'm': 60,
        'h': 60 * 60,
        'd': 60 * 60 * 24,
    }

    def __init__(self, after: str = DEFAULT_AFTER, before: str = DEFAULT_BEFORE) -> None:
        self.after_str = after
        self.before_str = before
        self.after = None
        self.before = None
        self.reference = datetime.now()

    def __str__(self) -> str:
        return f'({self.after}, {self.before})'

    @staticmethod
    def to_datetime(what: str, default: datetime) -> datetime:
        if not what:
            return default
        elif re.match(r'\d+$', what):
            # Digits only, epoch time.
            return datetime.fromtimestamp(int(what))
        match = re.match(r'(\d+)([dhms])$', what, IGNORECASE)
        if match:
            # Time delta relative to "UTC now", in the past.
            seconds = int(match.group(1)) * Interval.unit_seconds_map[match.group(2).lower()]
            d = datetime.now() - timedelta(seconds=seconds)
        else:
            # Attempt ISO 8601 string conversion. Exceptions are deliberately not caught.
            d = datetime.fromisoformat(what)
        return d

    def wraps(self, t: datetime) -> bool:
        if not self.before:
            self.after = self.to_datetime(self.after_str, datetime.fromtimestamp(0))
            self.before = self.to_datetime(self.before_str, datetime.fromisoformat('9999-12-31'))
        return self.after < t < self.before


class Config:
    """PostQF configuration elements."""

    def __init__(self) -> None:
        self.args = None
        self.interval = None
        self.qname_re = None
        self.rcpt_re = None
        self.reason_re = None
        self.sender_re = None

    def refresh(self, ns: Namespace) -> None:
        """Refresh config from parsed command line arguments."""
        self.args = ns
        self.interval = Interval(ns.after, ns.before)
        self.qname_re = compile(ns.qname, IGNORECASE)
        self.rcpt_re = compile(ns.rcpt, IGNORECASE)
        self.reason_re = compile(ns.reason, IGNORECASE)
        self.sender_re = compile(ns.sender, IGNORECASE)


# Shared configuration object
cf = Config()
