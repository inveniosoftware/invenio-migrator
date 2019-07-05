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

"""Celery records tests."""

from __future__ import absolute_import, print_function

import mock
import pytest

from invenio_records_files.models import RecordsBuckets
from invenio_files_rest.models import ObjectVersion, Bucket, BucketTag, \
    FileInstance
from invenio_records.models import RecordMetadata
from invenio_pidstore.models import PersistentIdentifier, RecordIdentifier

from invenio_migrator.tasks.records import import_record
from invenio_migrator.records import RecordDump


def test_import_record(app, db, dummy_location, record_dump, records_json,
                       resolver):
    """Test import record celery task."""
    assert RecordMetadata.query.count() == 0
    import_record(records_json[0], source_type='json')
    assert RecordMetadata.query.count() == 1
    pid, record = resolver.resolve('11782')
    assert record['_collections'] == []
    assert len(record['_files']) == 1
    assert ObjectVersion.get(
        record['_files'][0]['bucket'], record['_files'][0]['key'])

    import_record(records_json[1], source_type='marcxml')
    assert RecordMetadata.query.count() == 2
    pid, record = resolver.resolve('10')
    assert record['_collections'] == [
        "ALEPH Papers",
        "Articles & Preprints",
        "Experimental Physics (EP)",
        "CERN Divisions",
        "Atlantis Institute of Fictive Science",
        "CERN Experiments",
        "Preprints",
        "ALEPH",
    ]
    assert len(record['_files']) == 2


def test_failing_import_record(app, dummy_location, record_dump, records_json,
                               resolver):
    """Test failing a import record."""
    with mock.patch.object(RecordDump, 'is_deleted') as mock_create:
        mock_create.side_effect = Exception('error')
        with pytest.raises(Exception):
            import_record(records_json[0], source_type='json')

    assert RecordMetadata.query.all() == []
    assert PersistentIdentifier.query.all() == []
    assert RecordIdentifier.query.all() == []
    assert Bucket.query.all() == []
    assert BucketTag.query.all() == []
    assert ObjectVersion.query.all() == []
    # TODO enable when invenio-files-rest#167 is merged
    #  assert ObjectVersionTag.query.all() == []
    assert FileInstance.query.all() == []
    assert RecordsBuckets.query.all() == []
