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

"""Module tests."""

from __future__ import absolute_import, print_function

from invenio_pidstore.fetchers import FetchedPID

from invenio_migrator.records import RecordDump


def doi_fetcher(record_uuid, data):
    """Test fetcher."""
    if 'doi' in data:
        return FetchedPID(
            pid_type='doi', pid_value=data['doi'], provider=None
        )
    return None


def test_prepare_data_marcxml(records_json):
    """Test prepare data from marcxml."""
    d = RecordDump(records_json[0])
    d.prepare_revisions()
    assert len(d.revisions) == 1
    record = d.revisions[0][1]
    assert record['title_statement']['title']

    d = RecordDump(records_json[0], latest_only=True)
    d.prepare_revisions()
    assert len(d.revisions) == 1
    record = d.revisions[0][1]
    assert record['title_statement']['title']


def test_prepare_data_json(records_json):
    """Test prepare data from json."""
    d = RecordDump(records_json[0], source_type='json')
    d.prepare_revisions()
    assert len(d.revisions) == 1
    record = d.revisions[0][1]
    assert record['title']

    d = RecordDump(records_json[0], source_type='json', latest_only=True)
    d.prepare_revisions()
    assert len(d.revisions) == 1
    record = d.revisions[0][1]
    assert record['title']


def test_get_files(records_json):
    """Test get files."""
    d = RecordDump(records_json[0])
    d.prepare_files()
    assert len(d.files) == 1
    assert 'CERN_openlab_Parin_Porecha.pdf' in d.files


def test_record_property(app, db, records_json, record_db):
    """Test get files."""
    d = RecordDump(records_json[0])
    assert d.record


def test_record_property_no_record(app, db, records_json):
    """Test get files."""
    d = RecordDump(records_json[0])
    assert d.record is None


def test_pop_first_revision(records_json):
    """Test get files."""
    d = RecordDump(records_json[0])
    d.prepare_revisions()
    assert len(d.revisions) == 1
    assert d.pop_first_revision()
    assert len(d.revisions) == 0


def test_prepare_pids(app, db, records_json, record_db):
    """Test get files."""
    d = RecordDump(records_json[0], source_type='json')
    d.prepare_revisions()
    d.prepare_pids()
    assert len(d.pids) == 0

    d = RecordDump(
        records_json[0], source_type='json', pid_fetchers=[doi_fetcher])
    d.prepare_revisions()
    d.prepare_pids()
    assert len(d.pids) == 1


def test_missing_pids_pid_exist(app, db, records_json, record_pid):
    """Test get files."""
    d = RecordDump(
        records_json[0], source_type='json', pid_fetchers=[doi_fetcher])
    d.prepare_revisions()
    d.prepare_pids()
    assert len(d.pids) == 1
    assert len(d.missing_pids) == 0


def test_missing_pids(app, db, records_json, record_db):
    """Test get files."""
    d = RecordDump(
        records_json[0], source_type='json', pid_fetchers=[doi_fetcher])
    d.prepare_revisions()
    d.prepare_pids()
    assert len(d.pids) == 1
    assert len(d.missing_pids) == 1


def test_is_deleted(records_json):
    """Test get files."""
    d = RecordDump(records_json[0])
    d.prepare_revisions()
    assert not d.is_deleted()

    d = RecordDump(
        {'record': [{
            'json': {'collections': ['deleted']},
            'modification_datetime': '2014-10-10T10:10:10Z'
        }]},
        source_type='json'
    )
    d.prepare_revisions()
    assert d.is_deleted()
