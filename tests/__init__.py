"""
Copyright © 2022 Ralph Seichter

This file is part of PostQF.

PostQF is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

PostQF is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License along with PostQF.
If not, see <https://www.gnu.org/licenses/>.
"""
import re
from typing import List
from unittest import TestCase

from postqf import config


class PostqfTestCase(TestCase):
    data: dict

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        PostqfTestCase.data = {
            'queue_name': 'deferred',
            'queue_id': '4JgBRR6ypTz243v',
            'arrival_time': 1642751523,
            'message_size': 25405,
            'forced_expire': False,
            'sender': 'alice@example.org',
            'recipients': [
                {
                    'address': 'carol@example.com',
                    'delay_reason': 'connect to mail.example.com[1.2.3.4]:25: Connection timed out'
                },
                {
                    'address': 'ned@example.net',
                    'delay_reason': 'Recipient is over quota'
                },
            ]
        }

    @staticmethod
    def recipients() -> List[dict]:
        return PostqfTestCase.data['recipients']

    @staticmethod
    def config_re(name: str, regex: str) -> None:
        pattern = re.compile(regex, re.IGNORECASE)
        setattr(config.cf, name, pattern)
