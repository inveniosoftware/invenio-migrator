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
import zlib

from .bibdocfile import dump_bibdoc, get_modified_bibdoc_recids
from .utils import datetime_toutc, memoize


def _get_modified_recids_invenio12(from_date):
    """Get record ids for Invenio 1."""
    from invenio.search_engine import search_pattern
    from invenio.dbquery import run_sql
    return set((id[0] for id in run_sql(
        'select id from bibrec where modification_date >= %s',
        (from_date, ), run_on_slave=True))), search_pattern


def _get_modified_recids_invenio2(from_date):
    """Get record ids for Invenio 2."""
    from invenio.legacy.search_engine import search_pattern
    from invenio.modules.records.models import Record

    date = datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')
    return set(
        (x[0]
         for x in Record.query.filter(Record.modification_date >= date).values(
             Record.id))), search_pattern


@memoize
def _get_collection_restrictions(collection):
    """Get all restrictions for a given collection, users and fireroles."""
    try:
        from invenio.dbquery import run_sql
        from invenio.access_control_firerole import compile_role_definition
    except ImportError:
        from invenio.modules.access.firerole import compile_role_definition
        from invenio.legacy.dbquery import run_sql

    res = run_sql(
        'SELECT r.firerole_def_src, email '
        'FROM accROLE as r '
        'JOIN accROLE_accACTION_accARGUMENT ON r.id=id_accROLE '
        'JOIN accARGUMENT AS a ON a.id=id_accARGUMENT '
        'JOIN user_accROLE AS u ON r.id=u.id_accROLE '
        'JOIN user ON user.id=u.id_user '
        'WHERE a.keyword="collection" AND '
        'a.value=%s AND '
        'id_accACTION=(select id from accACTION where name="viewrestrcoll")',
        (collection, ), run_on_slave=True
    )
    fireroles = set()
    users = set()

    for f, u in res:
        fireroles.add(compile_role_definition(f))
        users.add(u)

    return {'fireroles': list(fireroles), 'users': users}


def get_modified_recids(from_date):
    """Get modified recids."""
    try:
        return _get_modified_recids_invenio12(from_date)
    except ImportError:
        return _get_modified_recids_invenio2(from_date)


def get_record_revisions(recid, from_date):
    """Get record revisions."""
    try:
        from invenio.dbquery import run_sql
    except ImportError:
        from invenio.legacy.dbquery import run_sql

    return run_sql(
        'SELECT job_date, marcxml '
        'FROM hstRECORD WHERE id_bibrec = %s AND job_date >= %s '
        'ORDER BY job_date ASC', (recid, from_date),
        run_on_slave=True)


def get_record_collections(recid):
    """Get all collections the record belong to."""
    try:
        from invenio.search_engine import (
            get_all_collections_of_a_record,
            get_restricted_collections_for_recid)
    except ImportError:
        from invenio.legacy.search_engine import (
            get_all_collections_of_a_record,
            get_restricted_collections_for_recid)

    collections = {
        'all':
        get_all_collections_of_a_record(recid, recreate_cache_if_needed=False),
    }
    collections['restricted'] = dict(
        (coll, _get_collection_restrictions(coll))
        for coll in get_restricted_collections_for_recid(
                recid, recreate_cache_if_needed=False))

    return collections


def dump_record_json(marcxml):
    """Dump JSON of record."""
    try:
        from invenio.modules.records.api import Record
        d = Record.create(marcxml, 'marc')
        return d.dumps(clean=True)
    except ImportError:
        from invenio.bibfield import create_record
        d = create_record(marcxml, master_format='marc')
        return d.dumps()


def get(query, from_date, **kwargs):
    """Get recids matching query and with changes."""
    recids, search_pattern = get_modified_recids(from_date)
    recids = recids.union(get_modified_bibdoc_recids(from_date))

    if query:
        recids = recids.intersection(
            set(search_pattern(p=query.encode('utf-8'))))

    return len(recids), recids


def dump(recid,
         from_date,
         with_json=False,
         latest_only=False,
         with_collections=False,
         **kwargs):
    """Dump MARCXML and JSON representation of a record.

    :param recid: Record identifier
    :param from_date: Dump only revisions from this date onwards.
    :param with_json: If ``True`` use old ``Record.create`` to generate the
        JSON representation of the record.
    :param latest_only: Dump only the last revision of the record metadata.
    :param with_collections: If ``True`` dump the list of collections that the
        record belongs to.
    :returns: List of versions of the record.
    """
    # Grab latest only
    if latest_only:
        revision_iter = [get_record_revisions(recid, from_date)[-1]]
    else:
        revision_iter = get_record_revisions(recid, from_date)

    # Dump revisions
    record_dump = dict(
        record=[],
        files=[],
        recid=recid,
        collections=get_record_collections(recid)
        if with_collections else None, )

    for revision_date, revision_marcxml in revision_iter:
        marcxml = zlib.decompress(revision_marcxml)
        record_dump['record'].append(
            dict(
                modification_datetime=datetime_toutc(revision_date)
                .isoformat(),
                marcxml=marcxml,
                json=dump_record_json(marcxml) if with_json else None, ))

    record_dump['files'] = dump_bibdoc(recid, from_date)

    return record_dump
