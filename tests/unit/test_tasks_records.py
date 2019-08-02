# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
