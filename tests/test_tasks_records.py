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

from invenio_files_rest.models import ObjectVersion
from invenio_records.models import RecordMetadata

from invenio_migrator.tasks.records import import_record


def test_import_record(app, db, dummy_location, record_dump, records_json,
                       resolver):
    """Test import record celery task."""
    assert RecordMetadata.query.count() == 0
    import_record(records_json[0], source_type='json')
    assert RecordMetadata.query.count() == 1
    pid, record = resolver.resolve('11782')
    assert len(record['files']) == 1
    assert ObjectVersion.get(
        record['files'][0]['bucket'], record['files'][0]['key'])
