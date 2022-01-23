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
import os
from logging import ERROR
from logging import Formatter
from logging import Logger
from logging import StreamHandler
from logging import getLogger

from postqf import PROGRAM
from postqf import VERSION

PROG_VER = f'{PROGRAM} {VERSION}'


def _level(log_level: str) -> int:
    i = getattr(logging, log_level.upper(), None)
    if isinstance(i, int):
        return i
    raise ValueError(f'Invalid log level "{log_level}" (use DEBUG, INFO, WARNING, ERROR or CRITICAL)')


def _logger() -> Logger:
    """Create a Logger object."""
    key = 'LOG_LEVEL'
    if key in os.environ:
        level = _level(os.environ.get(key))
    else:
        level = ERROR
    logger = getLogger(PROG_VER)
    handler = StreamHandler()
    handler.setFormatter(Formatter('%(asctime)s %(levelname)s %(message)s'))
    handler.setLevel(level)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


log = _logger()
