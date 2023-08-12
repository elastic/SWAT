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

"""Base class for attack Emulations."""

import argparse
import logging
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Optional

import yaml

from ..attack import lookup_technique_by_id
from ..base import SWAT, DEFAULT_EMULATION_ARTIFACTS_DIR
from ..logger import configure_emulation_logger
from ..misc import get_custom_argparse_formatter, validate_args


@dataclass
class AttackData:
    """Dataclass for ATT&CK Emulation"""
    tactic: str
    technique: list[str]
    _emulation_name: str
    _emulation_description: str

    def __str__(self) -> str:
        return f'{self.tactic}: {", ".join(self.technique)}'

    def _raw_technique_details(self) -> dict:
        """Get technique details from ATT&CK."""
        return {t: lookup_technique_by_id(t) for t in self.technique}

    def technique_details(self) -> dict:
        """Print technique details."""
        all_details = {}

        raw = self._raw_technique_details()
        for technique, details in raw.items():
            if not details:
                raise ValueError(f'Technique {technique} not found in ATT&CK data.')
            else:
                data = {
                    'id': technique,
                    'tactic': self.tactic,
                    'name': details.get('name'),
                    'description': details['description'].split('.')[0].strip(),
                    'emulation': self._emulation_name,
                    'emulation_description': self._emulation_description
                }
                all_details[technique] = data

        return all_details


class BaseEmulation:

    parser: Optional[argparse.ArgumentParser]
    techniques: list[str]

    def __init__(self, args: list, obj: SWAT, **extra) -> None:
        self.obj = obj
        self.logger = logging.getLogger(__name__)
        emulation_name = '.'.join(self.__module__.split('.')[2:])
        self.elogger = configure_emulation_logger(emulation_name, obj.config)
        self.econfig = self.load_emulation_config()
        self.attack_data = self.get_attack()
        self.artifacts_path = self.setup_artifacts_folder()

        assert self.parser, '"parser" must be implemented in each emulation command class'
        self.args = validate_args(self.parser, args)
        assert hasattr(self, 'techniques'), '"techniques" must be implemented in each emulation command class (or [])'

    def execute(self) -> None:
        raise NotImplementedError('The "execute" method must be implemented in each emulation class.')

    @classmethod
    @cache
    def get_attack(cls) -> AttackData:
        """Parse tactic and technique from path."""
        _, _, tactic, emulation_name = cls.__module__.split('.')
        techniques = [t.upper() for t in cls.techniques]
        return AttackData(tactic=tactic, technique=techniques, _emulation_name=emulation_name,
                          _emulation_description=cls.parser.description)

    def exec_str(self, description: str) -> str:
        """Return standard execution log string."""
        return f'Executing emulation for: [{self.attack_data}] {description}'

    @classmethod
    def help(cls):
        """Return the help message for the command."""
        assert cls.parser, '"parser" must be implemented in each emulation command class'
        return cls.parser.format_help()

    @classmethod
    def load_parser(cls, *args, **kwargs) -> argparse.ArgumentParser:
        """Return custom parser."""
        return get_custom_argparse_formatter(*args, **kwargs)

    @classmethod
    def load_emulation_config(cls) -> Optional[dict]:
        """Load YAML config file for emulation."""
        # Determine the path to the corresponding YAML file
        emulation_path = Path(cls.__module__.replace('.', '/'))
        config_file_path = emulation_path.with_suffix('.yaml')

        # Load the YAML file if it exists
        if config_file_path.exists():
            return yaml.safe_load(config_file_path.read_text())

    def setup_artifacts_folder(self) -> Path:
        """Create the artifacts folder if it doesn't exist."""
        DEFAULT_EMULATION_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        # TODO: fix
        self.logger.info(f'Artifacts folder created: {DEFAULT_EMULATION_ARTIFACTS_DIR}')
        return DEFAULT_EMULATION_ARTIFACTS_DIR
