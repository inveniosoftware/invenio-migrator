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

import datetime
import six

from werkzeug import import_string


def get(query, from_date, **kwargs):
    """Get record IDs matching the criteria.

    :param query:
    :param from_date:

    :returns: List of record IDs matching the criteria

    """
    try:
        from invenio.search_engine import search_pattern
        from invenio.dbquery import run_sql
        recids = [id[0] for id in run_sql(
            'select id from bibrec where modification_date >= %s',
            (from_date, ))]
        if query:
            return set(search_pattern(p=query)).intersection(recids)
        return recids
    except ImportError:
        from invenio.base.factory import create_app
        app = create_app()
        with app.app_context():
            from invenio.legacy.search_engine import search_pattern
            from invenio.modules.records.models import Record
            recids = Record.query.filter(
                Record.modification_date >= date).values(Record.id)
            if query:
                return set(search_pattern(p=query)).intersection(recids)
            return recids


def dump(recid, from_date, json_converter, **kwargs):
    """Dump MARCXML and JSON representation of a record.

    :param recid:
    :param from_date:
    :param json_converter: Function to convert the record to JSON

    :returns: List of versions of the record.

    """
    try:
        from invenio.bibedit_engine import get_record_revisions, \
            get_marcxml_of_revision_id
    except ImportError:
        from invenio.legacy.bibedit.engine import get_marcxml_of_revision_id
        from invenio.legacy.bibedit.db_layer import get_record_revisions

    if isinstance(json_converter, six.string_types):
        json_converter = import_string(json_converter)

    record_dump = dict(marcxml=[], json=[])
    date = datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')

    for revision in reversed(get_record_revisions(recid)):
        revision_date = datetime.datetime.strptime(
            revision[1], '%Y%m%d%H%M%S')
        if revision_date < date:
            continue
        marcxml = get_marcxml_of_revision_id(*revision)
        record_dump['marcxml'].append(marcxml)
        record_dump['json'].append(json_converter(marcxml))
    return record_dump
