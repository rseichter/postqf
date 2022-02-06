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
import os
import sys
import tempfile
from argparse import Namespace
from os.path import join
from tempfile import NamedTemporaryFile

from postqf.config import cf
from postqf.core import close_file
from postqf.core import count_rcpt
from postqf.core import format_output
from postqf.core import generate_report
from postqf.core import open_file
from postqf.core import process_files
from postqf.core import queue_name
from postqf.core import report_dict
from tests import PostqfTestCase


class Test(PostqfTestCase):
    def setUp(self) -> None:
        super().setUp()
        cf.refresh(Namespace(qname=None, rcpt=None, sender=None, reason=None))
        self.qdata = join(self.parentdir(__file__), 'qdata')

    def test_count_rcpt(self):
        rcpt = [
            {'a': 'alice@ham'},
            {'a': 'bob@ham'},
            {'a': 'chris@eggs'},
        ]
        count_rcpt(rcpt, 'a', separator='@')
        self.assertEqual(2, report_dict['ham'])
        self.assertEqual(1, report_dict['eggs'])

    def test_gen_report(self):
        d = {'a': 2, 'b': 4}
        with NamedTemporaryFile('wt', delete=False) as outfile:
            generate_report(d, outfile, reverse=True)
            outfile.close()
            with open(outfile.name, 'rt') as infile:
                self.assertEqual('4 b\n2 a\n', infile.read())
        os.unlink(outfile.name)

    def test_fmt_output(self):
        d = {'x': 'y', 'queue_id': 'abc'}
        self.assertEqual(r'{"x": "y", "queue_id": "abc"}', format_output(d))
        cf.queue_id = True
        self.assertEqual(r'abc', format_output(d))

    def test_open_close(self):
        tmp = join(tempfile.tempdir, f'{__name__}.tmp')
        f = open_file(tmp, 'w', None)
        self.assertIsNotNone(f)
        close_file(f)
        os.unlink(tmp)

    def test_open_close_std(self):
        f = open_file('-', 'w', sys.stdout)
        self.assertIsNotNone(f)
        close_file(f)

    def test_qname_absent(self):
        self.assertIsNone(queue_name({}))

    def test_qname_present(self):
        self.assertEqual('xyz', queue_name({'queue_name': 'xyz'}))

    def test_process_files(self):
        cf.infile = [self.qdata]
        cf.outfile = '-'
        self.assertTrue(process_files())

    def test_process_and_report_rcpt(self):
        cf.report_rcpt = True
        self.assertTrue(self._process())

    def test_process_and_report_rdom(self):
        cf.report_rdom = True
        self.assertTrue(self._process())

    def test_process_and_report_reason(self):
        cf.report_reason = True
        self.assertTrue(self._process())

    def _process(self) -> bool:
        tmp = NamedTemporaryFile(delete=False)
        tmp.close()
        cf.outfile = tmp.name
        cf.infile = [self.qdata]
        r = process_files()
        os.unlink(tmp.name)
        return r
