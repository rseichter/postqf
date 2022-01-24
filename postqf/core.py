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
import sys
from argparse import ArgumentParser
from argparse import Namespace
from typing import Optional

from postqf import PROGRAM
from postqf.config import Interval
from postqf.config import cf
from postqf.filter import arrival_match
from postqf.filter import rcpt_match
from postqf.filter import reason_match
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
    """Open a file handle unless it is standard input/output.

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
    """Process a single Postfix queue data record and write to the given
    output file if the record matches all user-specified filters.

    Args:
        qdata: Postfix queue data.
        outfile: Output file handle.
    """
    if (str_match(cf.qname_re, queue_name(qdata)) and
            str_match(cf.sender_re, qdata['sender']) and
            rcpt_match(qdata['recipients']) and
            reason_match(qdata['recipients']) and
            arrival_match(qdata['arrival_time'])):
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


def parse_args() -> Namespace:
    """Parse command line arguments."""
    parser = ArgumentParser(prog=PROGRAM, epilog=f'{PROG_VER} Copyright © 2022 Ralph Seichter')
    parser.add_argument('-i', dest='queue_id', action='store_true', help=f'ID output only.')
    group = parser.add_argument_group('Regular expression filters')
    group.add_argument('-d', dest='reason', metavar='REGEX', nargs='?', default='.', help=f'Delay reason filter.')
    group.add_argument('-q', dest='qname', metavar='REGEX', nargs='?', default='.', help=f'Queue name filter.')
    group.add_argument('-r', dest='rcpt', metavar='REGEX', nargs='?', default='.', help=f'Recipient address filter.')
    group.add_argument('-s', dest='sender', metavar='REGEX', nargs='?', default='.', help=f'Sender address filter.')
    group = parser.add_argument_group('Arrival time filters')
    group.add_argument('-a', dest='after', metavar='TS', nargs='?', default=Interval.DEFAULT_AFTER,
                       help=f'Message arrived after TS.')
    group.add_argument('-b', dest='before', metavar='TS', nargs='?', default=Interval.DEFAULT_BEFORE,
                       help=f'Message arrived before TS.')
    parser.add_argument('-o', dest='outfile', metavar='PATH', nargs='?', default='-',
                        help='Output file. Use a dash "-" for standard output.')
    parser.add_argument('infile', metavar='PATH', nargs='*', default='-',
                        help='Input file. Use a dash "-" for standard input.')
    return parser.parse_args()


def main() -> None:
    cf.refresh(parse_args())
    process_files()
