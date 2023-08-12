#
# Licensed to Elasticsearch under one or more contributor
# license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Elasticsearch licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

"""Base command functionality."""

import argparse
import logging
from typing import List

from ..base import SWAT
from ..misc import get_custom_argparse_formatter


class BaseCommand:

    def __init__(self, command: str = None, args: List[str] = list, obj: SWAT = None) -> None:
        self.command = command
        self.args = args
        self.logger = logging.getLogger(__name__)
        self.obj = obj

    def execute(self) -> None:
        raise NotImplementedError('The "execute" method must be implemented in each command class.')

    @classmethod
    def custom_help(cls) -> str:
        """Return custom help string."""
        raise NotImplementedError('The "custom_help" method must be implemented in each command class.')

    @classmethod
    def load_parser(cls, *args, **kwargs) -> argparse.ArgumentParser:
        """Return custom parser."""
        return get_custom_argparse_formatter(*args, **kwargs)
