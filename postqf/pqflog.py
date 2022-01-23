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
from logging import Formatter
from logging import INFO
from logging import Logger
from logging import StreamHandler
from logging import getLogger

from postqf import PROGRAM
from postqf import VERSION

PROG_VER = f'{PROGRAM} {VERSION}'


def _create_logger() -> Logger:
    """Create a Logger object."""
    logger = getLogger(PROG_VER)
    handler = StreamHandler()
    handler.setFormatter(Formatter('%(asctime)s %(levelname)s %(message)s'))
    log_level = INFO
    handler.setLevel(log_level)
    logger.addHandler(handler)
    logger.setLevel(log_level)
    return logger


def set_log_level(s: str) -> None:
    level = getattr(logging, s.upper(), None)
    if not isinstance(level, int):
        raise ValueError(f'Invalid log level "{s}" (use DEBUG, INFO, WARNING, ERROR or CRITICAL)')
    log.setLevel(level)


log = _create_logger()
