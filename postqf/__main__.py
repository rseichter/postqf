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
import json
import logging
import re
import sys
from argparse import ArgumentParser
from argparse import Namespace
from logging import Logger
from logging import StreamHandler
from logging import getLogger
from re import Pattern
from typing import List
from typing import Optional

from postqf import PROGRAM
from postqf import VERSION


def create_logger(log_level: int) -> Logger:
    """Create a Logger object with the given log level."""
    logger = getLogger(__name__)
    handler = StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    handler.setLevel(log_level)
    logger.addHandler(handler)
    logger.setLevel(log_level)
    return logger


def close_file(file):
    """Close file handle unless it is standard input/output."""
    if file:
        name = getattr(file, 'name', None)
        if name and name not in ['<stdin>', '<stdout>']:
            file.close()


def open_file(path: str, mode: str, dash_file):
    """Open a file handle.

    Args:
        path: File name/path or "-".
        mode: Mode passed to builtins.open().
        dash_file: Returned if path equals "-".
    """
    if path == '-':
        return dash_file
    return open(path, mode=mode, encoding='utf-8')


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
    """Return True if one of the recipients matches both address and delay reason.

    Args:
        recipients: List of Postfix recipient data.
    """
    address_match, reason_match = False, False
    for rcpt in recipients:
        if not rcpt_re.search(rcpt['address']):
            log.debug(f'No match for {rcpt_re.pattern}')
            continue
        address_match = True
        if 'delay_reason' in rcpt and reason_re.search(rcpt['delay_reason']):
            reason_match = True
            break
        log.debug(f'No match for {reason_re.pattern}')
    return address_match and reason_match


def format_output(data: dict):
    """Return either the full input data or only the queue_id element,
    depending on command line arguments.

    Args:
        data: Postfix recipient data.
    """
    if args.queue_id:
        return data['queue_id']
    return data


def queue_name(data: dict) -> Optional[str]:
    """Extract the Postfix queue name. This also serves as a sanity check,
    because valid queue data must contain this attribute.

    Args:
        data: Single queue entry produced by "postqueue -j".
    """
    name = 'queue_name'
    if name in data:
        return data[name]
    log.error(f'Malformed input data: element "{name}" is missing')


def process_record(qdata: dict, outfile) -> None:
    """Process a single Postfix queue data record and write to the specified output file.

    Args:
        qdata: Postfix queue data.
        outfile: Output file handle.
    """
    name = queue_name(qdata)
    if not (str_match(qname_re, name) and
            str_match(sender_re, qdata['sender']) and
            rcpt_match(qdata['recipients'])):
        return
    print(format_output(qdata), file=outfile)


def process_files() -> None:
    """Process all given input files in order."""
    outfile = open_file(args.outfile, 'wt', sys.stdout)
    for path in args.infile:
        infile = open_file(path, 'rt', sys.stdin)
        try:
            for line in infile:
                process_record(json.loads(line), outfile)
        except Exception as e:
            log.exception(e)
        finally:
            close_file(infile)
    close_file(outfile)


def parse_args() -> Namespace:
    """Parse command line arguments."""
    p = ArgumentParser(prog=PROGRAM, epilog=f'{PROGRAM} {VERSION} Copyright © 2022 Ralph Seichter')
    p.add_argument('-d', dest='reason', metavar='REGEX', nargs='?', default='.', help=f'Delay reason filter')
    p.add_argument('-q', dest='qname', metavar='REGEX', nargs='?', default='.', help=f'Queue name filter')
    p.add_argument('-r', dest='recipient', metavar='REGEX', nargs='?', default='.', help=f'Recipient address filter')
    p.add_argument('-s', dest='sender', metavar='REGEX', nargs='?', default='.', help=f'Sender address filter')
    p.add_argument('-i', dest='queue_id', action='store_true', help=f'Output only queue IDs')
    p.add_argument('-l', dest='level', metavar='LEVEL', nargs='?', default='WARNING',
                   help=f'Log level (default: WARNING)')
    p.add_argument('-o', dest='outfile', metavar='PATH', nargs='?', default='-',
                   help='Input file. Use a dash "-" for standard output.')
    p.add_argument('infile', metavar='PATH', nargs='*', default='-',
                   help='Input file. Use a dash "-" for standard input.')
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    level = getattr(logging, args.level.upper(), None)
    if not isinstance(level, int):
        raise ValueError(f'Invalid log level "{args.level}" (use DEBUG, INFO, WARNING, ERROR or CRITICAL)')
    log = create_logger(level)
    qname_re = re.compile(args.qname, re.IGNORECASE)
    rcpt_re = re.compile(args.recipient, re.IGNORECASE)
    reason_re = re.compile(args.reason, re.IGNORECASE)
    sender_re = re.compile(args.sender, re.IGNORECASE)
    process_files()
