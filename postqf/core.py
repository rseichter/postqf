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


def format_output(data: dict) -> str:
    """Return either the full input data (JSON) or only the queue_id element,
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


def count_rcpt(recipients: list, attribute: str, to_lower: bool = False, separator: str = '') -> None:
    """Collect recipient attribute data for a report.

    Args:
        recipients: Dictionary of recipient data.
        attribute: The attribute to count.
        to_lower: Convert attribute value to lower case?
        separator: If specified, split attribute values at the given substring and pick the second element.
        This is useful for extracting domain names from address-type attributes.
    """
    for r in recipients:
        if attribute in r:
            count_key(r[attribute], to_lower=to_lower, separator=separator)


def count_key(key: str, to_lower: bool = False, separator: str = '') -> None:
    """Collect sender address data for a report.

    Args:
        key: Message sender address.
        to_lower: Convert key to lower case?
        separator: If specified, split attribute values at the given substring and pick the second element.
        This is useful for extracting domain names from address-type attributes.
    """
    global report_dict
    if key and separator:
        key = key.split(separator)[1]
    if key:
        if to_lower:
            key = key.lower()
        if key in report_dict:
            report_dict[key] += 1
        else:
            report_dict[key] = 1


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
            count_rcpt(qdata['recipients'], 'address', to_lower=True, separator='@')
        elif cf.report_rcpt:
            count_rcpt(qdata['recipients'], 'address', to_lower=True)
        elif cf.report_reason:
            count_rcpt(qdata['recipients'], 'delay_reason')
        elif cf.report_sdom:
            count_key(qdata['sender'], to_lower=True, separator='@')
        elif cf.report_sender:
            count_key(qdata['sender'], to_lower=True)
        else:
            print(format_output(qdata), file=outfile)


def process_files() -> bool:
    """Process all given input files in order.

    Returns True to indicate success, False in case of exceptions.
    """
    ex = None
    outfile = open_file(cf.outfile, 'wt', sys.stdout)
    for path in cf.infile:
        infile = open_file(path, 'rt', sys.stdin)
        try:
            for line in infile:
                process_record(json.loads(line), outfile)
        except Exception as e:  # pragma: no cover
            log.exception(e)
            ex = e
        finally:
            close_file(infile)
    global report_dict
    if report_dict:
        generate_report(report_dict, outfile)
    close_file(outfile)
    return not isinstance(ex, Exception)


def parse_args() -> Namespace:  # pragma: no cover
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
    group.add_argument('--report-sdom', dest='report_sdom', action='store_true', help='Report sender domains.')
    group.add_argument('--report-sender', dest='report_sender', action='store_true', help='Report sender addresses.')
    return parser.parse_args()


def main() -> None:  # pragma: no cover
    """Execution starts here."""
    cf.refresh(parse_args())
    process_files()
