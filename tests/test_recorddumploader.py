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

from datetime import datetime

import pytest
from invenio_files_rest.models import Bucket, BucketTag, FileInstance, \
    ObjectVersion
from invenio_pidstore.models import PersistentIdentifier, PIDStatus, \
    RecordIdentifier
from invenio_records.api import Record
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from invenio_migrator.records import RecordDumpLoader


def test_new_record(app, db, dummy_location, record_dump, resolver):
    """Test creation of new record."""
    RecordDumpLoader.create(record_dump)
    pid, record = resolver.resolve('11782')
    # Basic some test that record exists
    assert record['title']
    assert record.created == datetime(2014, 10, 13, 8, 27, 47)
    # Test that this is a completely new record
    assert len(record.revisions) == 2
    pytest.raises(IntegrityError, RecordIdentifier.insert, 11782)
    # Test the PIDs are extracted and created
    assert PersistentIdentifier.get('doi', '10.5281/zenodo.11782')

    assert len(record['files']) == 1
    f = record['files'][0]
    obj = ObjectVersion.get(f['bucket'], f['key'])
    assert obj.file.checksum == f['checksum']
    assert obj.file.size == f['size']

    assert BucketTag.get_value(f['bucket'], 'record') == str(record.id)


def test_update_record(app, db, dummy_location, record_dump, record_db,
                       resolver, record_file):
    """Test update of a record."""
    # Smoke test
    record_db['files'] = [record_file]
    record_db.commit()
    db.session.commit()

    pytest.raises(IntegrityError, RecordIdentifier.insert, 11782)
    # Update record instead of create a new
    RecordDumpLoader.create(record_dump)
    pid, record = resolver.resolve('11782')
    # Basic some test that record exists
    assert record['title']
    assert record.created == datetime(2014, 10, 13, 8, 27, 47)
    # Test that old revisions are kept
    assert len(record.revisions) == 4
    # Test the PIDs are extracted and created
    assert PersistentIdentifier.get('doi', '10.5281/zenodo.11782')

    assert Bucket.query.count() == 1
    assert ObjectVersion.query.filter_by(is_head=True).count() == 1
    assert FileInstance.query.count() == 2

    assert len(record['files']) == 1
    f = record['files'][0]
    obj = ObjectVersion.get(f['bucket'], f['key'])
    assert obj.file.checksum != record_file['checksum']
    assert obj.file.size != record_file['size']


def test_deleted_record(app, db, dummy_location, record_dump, resolver):
    """Test init."""
    record_dump.data['record'][0]['json']['collections'] = ['deleted']
    record_dump.prepare_revisions()
    assert record_dump.is_deleted()

    RecordDumpLoader.create(record_dump)

    pid = PersistentIdentifier.get('recid', '11782')
    assert pid.status == PIDStatus.DELETED
    pid = PersistentIdentifier.get('doi', '10.5281/zenodo.11782')
    assert pid.status == PIDStatus.DELETED

    Record.get_record(pid.object_uuid, with_deleted=True)
    pytest.raises(
        NoResultFound, Record.get_record, pid.object_uuid)

    assert Bucket.query.count() == 1
    assert ObjectVersion.query.count() == 1
    assert FileInstance.query.count() == 1

    bucket = Bucket.query.all()[0]
    assert bucket.deleted
