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
from typing import List
from typing import Pattern

from postqf.config import cf
from postqf.logstuff import log


def str_match(regex: Pattern, candidate: str) -> bool:
    """Return True if the candidate matches the regular expression.

    Args:
        regex: Pre-compiled regular expression.
        candidate: String to match against the RE.
    """
    if candidate and regex.search(candidate):
        return True
    log.debug(f'"{candidate}" does not match "{regex.pattern}"')
    return False


def rcpt_match(recipients: List[dict]) -> bool:
    """Return True if one of the recipients matches.

    Args:
        recipients: List of Postfix recipient data.
    """
    for recipient in recipients:
        if cf.rcpt_re.search(recipient['address']):
            return True
    log.debug(f'No match for {cf.rcpt_re.pattern}')
    return False


def reason_match(recipients: List[dict]) -> bool:
    """Return True if one of the delay reasons matches, or if there is no delay
    reason available for any recipient and no reason filter has been specified.

    Args:
        recipients: List of Postfix recipient data.
    """
    for recipient in recipients:
        if 'delay_reason' in recipient:
            if cf.reason_re.search(recipient['delay_reason']):
                return True
        elif cf.reason_re.pattern == '.':
            # Queue data contains no delay reason and no reason filter was specified.
            return True
    log.debug(f'No match for {cf.reason_re.pattern}')
    return False


def arrival_match(epoch_time: int) -> bool:
    """Return True if the specified time matches the filter.

    Args:
        epoch_time: Message arrival time in seconds since the Unix epoch.
    """
    arrived = datetime.fromtimestamp(epoch_time)
    return cf.interval.wraps(arrived)
