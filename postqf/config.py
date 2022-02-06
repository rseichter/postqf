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
from re import Pattern
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
    def to_datetime(string: str, default: datetime) -> datetime:
        """Convert a string into a datetime object."""
        if not string:
            return default
        elif re.match(r'\d+$', string):
            # Digits only, epoch time.
            return datetime.fromtimestamp(int(string))
        match = re.match(r'(\d+)([dhms])$', string, IGNORECASE)
        if match:
            # Time delta relative to "UTC now", in the past.
            seconds = int(match.group(1)) * Interval.unit_seconds_map[match.group(2).lower()]
            d = datetime.now() - timedelta(seconds=seconds)
        else:
            # Attempt ISO 8601 string conversion. Exceptions are deliberately not caught.
            d = datetime.fromisoformat(string)
        return d

    def includes(self, t: datetime) -> bool:
        """Return True if a datetime object is indluded in the configured interval."""
        if not self.before:
            self.after = self.to_datetime(self.after_str, datetime.fromtimestamp(0))
            self.before = self.to_datetime(self.before_str, datetime.fromisoformat('9999-12-31'))
        return self.after < t < self.before


class Config:
    """PostQF configuration elements."""

    def __init__(self) -> None:
        self.infile = None
        self.interval = None
        self.outfile = None
        self.qname_re = None
        self.queue_id = None
        self.rcpt_re = None
        self.reason_re = None
        self.report_rcpt = False
        self.report_rdom = False
        self.report_reason = False
        self.report_sender = False
        self.sender_re = None

    @staticmethod
    def re_compile(regex: str, default: str = '.') -> Pattern:
        """Compile a regex if available, '.' otherwise."""
        if not regex:
            regex = default
        return compile(regex, IGNORECASE)

    @staticmethod
    def get_attr(ns: Namespace, name: str, default):
        """Return a namespace attribute if available, a default value otherwise."""
        value = getattr(ns, name, None)
        if value:
            return value
        return default

    def refresh(self, ns: Namespace) -> None:
        """Refresh config from parsed command line arguments."""
        self.infile = self.get_attr(ns, 'infile', ['-'])
        self.outfile = self.get_attr(ns, 'outfile', '-')
        self.queue_id = self.get_attr(ns, 'queue_id', False)
        self.report_rcpt = self.get_attr(ns, 'report_rcpt', False)
        self.report_rdom = self.get_attr(ns, 'report_rdom', False)
        self.report_reason = self.get_attr(ns, 'report_reason', False)
        self.report_sender = self.get_attr(ns, 'report_sender', False)

        self.qname_re = Config.re_compile(ns.qname)
        self.rcpt_re = Config.re_compile(ns.rcpt)
        self.reason_re = Config.re_compile(ns.reason)
        self.sender_re = Config.re_compile(ns.sender)

        after = self.get_attr(ns, 'after', Interval.DEFAULT_AFTER)
        before = self.get_attr(ns, 'before', Interval.DEFAULT_BEFORE)
        self.interval = Interval(after, before)


# Shared configuration object
cf = Config()
