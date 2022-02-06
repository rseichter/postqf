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
from postqf import VERSION
from postqf.config import cf
from postqf.filter import arrival_match
from postqf.filter import rcpt_match
from postqf.filter import reason_match
from postqf.filter import str_match
from postqf.logstuff import log

report_dict = {}


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
    if cf.queue_id:
        return data['queue_id']
    return json.dumps(data)


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


def count_rcpt(recipients: dict, attribute: str, separator: str = '') -> None:
    """Count recipient attribute data for a report.

    Args:
        recipients: Dictionary of recipient data.
        attribute: The attribute to count.
        separator: If specified, split attribute values at the given substring and pick the second element.
        This is useful for extracting domain names from address-type attributes.
    """
    global report_dict
    for recipient in recipients:
        if attribute not in recipient:
            continue
        v: str = recipient[attribute]
        if v and separator:
            v = v.split(separator)[1]
        if not v:
            continue
        if v in report_dict:
            report_dict[v] += 1
        else:
            report_dict[v] = 1


def generate_report(data: dict, outfile, reverse: bool = False) -> None:
    """Generate report and write it to the given output file.

    Args:
        data: Report data dictionary.
        outfile: Output file handle.
        reverse: Sort data in reverse order?
    """
    for i in sorted(data.items(), key=lambda _item: _item[1], reverse=reverse):
        print(i[1], i[0], file=outfile)


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
        if cf.report_rdom:
            count_rcpt(qdata['recipients'], 'address', separator='@')
        elif cf.report_rcpt:
            count_rcpt(qdata['recipients'], 'address')
        elif cf.report_reason:
            count_rcpt(qdata['recipients'], 'delay_reason')
        else:
            print(format_output(qdata), file=outfile)


def process_files() -> None:
    """Process all given input files in order."""
    outfile = open_file(cf.outfile, 'wt', sys.stdout)
    for path in cf.infile:
        infile = open_file(path, 'rt', sys.stdin)
        try:
            for line in infile:
                process_record(json.loads(line), outfile)
        except Exception as e:
            log.exception(e)
        finally:
            close_file(infile)
    global report_dict
    if report_dict:
        generate_report(report_dict, outfile)
    close_file(outfile)


def parse_args() -> Namespace:
    """Parse command line arguments."""
    parser = ArgumentParser(prog=PROGRAM, epilog=f'{PROGRAM} {VERSION} Copyright © 2022 Ralph Seichter')
    parser.add_argument('-i', dest='queue_id', action='store_true', help='ID output only.')
    group = parser.add_argument_group('Regular expression filters')
    group.add_argument('-d', dest='reason', metavar='REGEX', help='Delay reason filter.')
    group.add_argument('-q', dest='qname', metavar='REGEX', help='Queue name filter.')
    group.add_argument('-r', dest='rcpt', metavar='REGEX', help='Recipient address filter.')
    group.add_argument('-s', dest='sender', metavar='REGEX', help='Sender address filter.')
    group = parser.add_argument_group('Arrival time filters')
    group.add_argument('-a', dest='after', metavar='TS', help='Message arrived after TS.')
    group.add_argument('-b', dest='before', metavar='TS', help='Message arrived before TS.')
    parser.add_argument('-o', dest='outfile', metavar='OUTFILE',
                        help='Output file. Use a dash "-" for standard output.')
    parser.add_argument('infile', metavar='FILE', nargs='*', help='Input file. Use a dash "-" for standard input.')
    group = parser.add_argument_group('Report generators').add_mutually_exclusive_group()
    group.add_argument('--report-rcpt', dest='report_rcpt', action='store_true', help='Report recipient addresses.')
    group.add_argument('--report-rdom', dest='report_rdom', action='store_true', help='Report recipient domains.')
    group.add_argument('--report-reason', dest='report_reason', action='store_true', help='Report delay reasons.')
    return parser.parse_args()


def main() -> None:
    """Execution starts here."""
    cf.refresh(parse_args())
    process_files()
