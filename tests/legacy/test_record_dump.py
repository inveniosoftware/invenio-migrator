# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Test legacy record dump."""

from click.testing import CliRunner

from invenio_migrator.legacy.cli import dump as dump_cli
from invenio_migrator.legacy.records import (
    dump as dump_record,
    get as get_record
)


def test_dump_record():
    """Test single record dump."""
    record_dump = dump_record(
        10, '1970-01-01 00:00:00', latest_only=False,
        with_json=False, with_collections=True)

    assert record_dump

    assert record_dump['recid'] == 10
    assert record_dump['collections'] == [
        'ALEPH Papers',
        'Articles & Preprints',
        'Experimental Physics (EP)',
        'CERN Divisions',
        'Atlantis Institute of Fictive Science',
        'CERN Experiments',
        'Preprints',
        'ALEPH'
    ]
    assert len(record_dump['files']) == 2
    assert len(record_dump['record']) == 2
    assert 'marcxml' in record_dump['record'][0]
    assert 'json' in record_dump['record'][0]
    assert record_dump['record'][0]['json'] is None
    assert 'modification_datetime' in record_dump['record'][0]

    record_dump_latest = dump_record(
        10, '1970-01-01 00:00:00', with_json=False, latest_only=True)

    assert record_dump_latest['record'][0] == record_dump['record'][1]

    record_dump = dump_record(
        10, '1970-01-01 00:00:00', latest_only=False,
        with_json=False, with_collections=False)

    assert record_dump['collections'] is None

    record_dump = dump_record(
        10, '1970-01-01 00:00:00', latest_only=False,
        with_json=True, with_collections=True)
    assert record_dump['record'][0]['json']['recid'] == 10
    assert len(record_dump['record'][0]['json']['authors']) == 315


def test_get_record():
    """Test get record."""
    records = get_record('Ellis', '1970-01-01 00:00:00')
    assert records[0] == 13
    assert records[1] == set(
        [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 118, 47])


def test_cli():
    """Test CLI."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            dump_cli, ['records', '-q', 'Ellis', '--with-json'])
        assert result.exit_code == 0
