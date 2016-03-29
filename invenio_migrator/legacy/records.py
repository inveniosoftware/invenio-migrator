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

"""Record and BibDocFile dump functions."""

from __future__ import absolute_import, print_function

import datetime

from .bibdocfile import dump_bibdoc, get_modified_bibdoc_recids
from .utils import datetime_toutc


def _get_modified_recids_invenio12(from_date):
    """Get record ids for Invenio 1."""
    from invenio.search_engine import search_pattern
    from invenio.dbquery import run_sql
    return set((id[0] for id in run_sql(
        'select id from bibrec where modification_date >= %s',
        (from_date, )))), search_pattern


def _get_modified_recids_invenio2(from_date):
    """Get record ids for Invenio 2."""
    from invenio.legacy.search_engine import search_pattern
    from invenio.modules.records.models import Record

    date = datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')
    return set((x[0] for x in Record.query.filter(
        Record.modification_date >= date).values(Record.id))), search_pattern


def get_modified_recids(from_date):
    """Get modified recids."""
    try:
        return _get_modified_recids_invenio12(from_date)
    except ImportError:
        return _get_modified_recids_invenio2(from_date)


def _import_get_revisions():
    """Wrap imports."""
    try:
        from invenio.bibedit_engine import get_record_revisions, \
            get_marcxml_of_revision_id
    except ImportError:
        from invenio.legacy.bibedit.engine import get_marcxml_of_revision_id
        from invenio.legacy.bibedit.db_layer import get_record_revisions

    return get_record_revisions, get_marcxml_of_revision_id


def dump_record_json(marcxml):
    """Dump JSON of record."""
    try:
        from invenio.modules.records.api import Record
        d = Record.create(marcxml, 'marc')
        return d.dumps(clean=True)
    except ImportError:
        return None


def get(query, from_date, **kwargs):
    """Get recids matching query and with changes."""
    recids, search_pattern = get_modified_recids(from_date)
    recids = recids.union(get_modified_bibdoc_recids(from_date))

    if query:
        return recids.intersection(set(search_pattern(p=query)))

    return len(recids), recids


def dump(recid, from_date, with_json=True, latest_only=False, **kwargs):
    """Dump MARCXML and JSON representation of a record.

    :param recid: Record identifier
    :param from_date: Dump only revisions from this date onwards.
    :param json_converter: Function to convert the record to JSON
    :returns: List of versions of the record.
    """
    get_record_revisions, get_marcxml_of_revision_id = _import_get_revisions()

    date = datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')

    # Grab latest only
    if latest_only:
        revision_iter = [get_record_revisions(recid)[0]]
    else:
        revision_iter = reversed(get_record_revisions(recid))

    # Dump revisions
    record_dump = dict(record=[], files=[], recid=recid)

    for revision in revision_iter:
        revision_date = datetime.datetime.strptime(
            revision[1], '%Y%m%d%H%M%S')
        if date is not None and revision_date < date:
            continue

        marcxml = get_marcxml_of_revision_id(*revision)

        record_dump['record'].append(dict(
            modification_datetime=datetime_toutc(revision_date).isoformat(),
            marcxml=marcxml,
            json=dump_record_json(marcxml) if with_json else None,
        ))

    record_dump['files'] = dump_bibdoc(recid, from_date)

    return record_dump
