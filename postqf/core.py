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
import re
import sys
from argparse import ArgumentParser
from argparse import Namespace
from datetime import datetime
from datetime import timedelta
from typing import Optional

from postqf import PROGRAM
from postqf.config import Cutoff
from postqf.config import cf
from postqf.filter import arrival_match
from postqf.filter import rcpt_match
from postqf.filter import str_match
from postqf.logstuff import PROG_VER
from postqf.logstuff import log


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


def format_output(data: dict):
    """Return either the full input data or only the queue_id element,
    depending on command line arguments.

    Args:
        data: Postfix recipient data.
    """
    if cf.args.queue_id:
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
    if not (str_match(cf.qname_re, name) and
            str_match(cf.sender_re, qdata['sender']) and
            rcpt_match(qdata['recipients']) and
            arrival_match(qdata['arrival_time'])):
        return
    print(format_output(qdata), file=outfile)


def process_files() -> None:
    """Process all given input files in order."""
    outfile = open_file(cf.args.outfile, 'wt', sys.stdout)
    for path in cf.args.infile:
        infile = open_file(path, 'rt', sys.stdin)
        try:
            for line in infile:
                process_record(json.loads(line), outfile)
        except Exception as e:
            log.exception(e)
        finally:
            close_file(infile)
    close_file(outfile)


def parse_cutoff(delta: str, before: bool) -> Cutoff:
    """Parse the after/before command line argument."""
    unit_to_seconds = {
        # Map human-readable time unit string to seconds
        's': 1,
        'm': 60,
        'h': 60 * 60,
        'd': 60 * 60 * 24,
    }
    if delta is None:
        seconds = 0
        log.debug('No time filter specified')
    else:
        pattern = r'^(\d+)([dhms])$'
        match = re.search(pattern, delta, re.IGNORECASE)
        if not match:
            raise ValueError(f'Time filter {delta} does not match {pattern}')
        seconds = int(match.group(1)) * unit_to_seconds[match.group(2).lower()]
    threshold = datetime.utcnow() - timedelta(seconds=seconds)
    log.debug(f'Arrival time threshold {threshold}')
    cutoff = Cutoff(before=before, threshold=threshold, always_true=(delta is None))
    return cutoff


def parse_args() -> Namespace:
    """Parse command line arguments."""
    parser = ArgumentParser(prog=PROGRAM, epilog=f'{PROG_VER} Copyright © 2022 Ralph Seichter')
    parser.add_argument('-i', dest='queue_id', action='store_true', help=f'ID output only')
    group = parser.add_argument_group('Regular expression filters')
    group.add_argument('-d', dest='reason', metavar='REGEX', nargs='?', default='.', help=f'Delay reason filter')
    group.add_argument('-q', dest='qname', metavar='REGEX', nargs='?', default='.', help=f'Queue name filter')
    group.add_argument('-r', dest='rcpt', metavar='REGEX', nargs='?', default='.', help=f'Recipient address filter')
    group.add_argument('-s', dest='sender', metavar='REGEX', nargs='?', default='.', help=f'Sender address filter')
    group = parser.add_argument_group('Arrival time filters (mutually exclusive)').add_mutually_exclusive_group()
    group.add_argument('-a', dest='after', metavar='TS', nargs='?', help=f'Message arrived after TS')
    group.add_argument('-b', dest='before', metavar='TS', nargs='?', help=f'Message arrived before TS')
    parser.add_argument('-o', dest='outfile', metavar='PATH', nargs='?', default='-',
                        help='Output file. Use a dash "-" for standard output.')
    parser.add_argument('infile', metavar='PATH', nargs='*', default='-',
                        help='Input file. Use a dash "-" for standard input.')
    return parser.parse_args()


def main() -> None:
    cf.args = parse_args()
    cf.qname_re = re.compile(cf.args.qname, re.IGNORECASE)
    cf.rcpt_re = re.compile(cf.args.rcpt, re.IGNORECASE)
    cf.reason_re = re.compile(cf.args.reason, re.IGNORECASE)
    cf.sender_re = re.compile(cf.args.sender, re.IGNORECASE)
    if cf.args.before:
        cf.cutoff = parse_cutoff(cf.args.before, True)
    else:
        cf.cutoff = parse_cutoff(cf.args.after, False)
    process_files()
