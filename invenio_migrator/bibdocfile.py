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

import datetime


def get(record_query, from_date, **kwargs):
    """Get BibDoc IDs.

    :param record_query: Look only for BibDocs attached to the records
        matching this query.
    :param from_date: Look for BibDocs modified since this date.

    :returns: List of  BibDoc IDs matching the criteria.
    """
    from .records import get as get_records
    try:
        from invenio.dbquery import run_sql
        from invenio.bibdocfile import BibRecDocs
        def _get_bibdocs():
            return [id[0] for id in run_sql(
                'select id from bibdoc where modification_date >=%s',
                (from_date, ))]
    except ImportError:
        from invenio.base.factory import create_app
        from invenio.legacy.bibdocfile.api import BibRecDocs
        def _get_bibdocs():
            date = datetime.datetime.strptime(
                from_date, '%Y-%m-%d %H:%M:%S')
            app = create_app()
            with app.app_context():
                from invenio.modules.editor.models import Bibdoc
                return BibDoc.query.filter(
                    BibDoc.modification_date >= date).values(BibDoc.id)

    recids = get_records(record_query, from_date)
    bibdoc_from_records = [bibdoc.id for recid in recids
        for bibdoc in BibRecDocs(recid).list_bibdocs()]

    return set(bibdoc_from_records).intersection(_get_bibdocs())


def dump(docid, from_date, **kwargs):
    """Dump all BibDoc metadata.

    :param docid: BibDoc ID
    :param from_date: Dump only BibDoc revisions newer than this date.

    :returns: List of version of the BibDoc formatted as a dict
    """
    try:
        from invenio.bibdocfile import BibDoc
    except ImportError:
        from invenio.legacy.bibdocfile.api import BibDoc

    bibdocfile_dump = []
    bibdoc = BibDoc(docid)
    date = datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')
    for version in bibdoc.list_versions():
        bibdoc_version = bibdoc.list_version_files(version)
        for f in bibdoc_version:
            if f.is_icon() or f.md < date:
                # Don't care about icons
                # Don't care about files not modified since from_date
                continue
            bibdocfile_dump.append(dict(
                bibdocid=f.get_bibdocid(),
                checksum=f.get_checksum(),
                comment=f.get_comment(),
                copyright=f.get_copyright() if hasattr(g, 'get_copyright') else '',
                creation_date=f.cd.strftime("%Y-%m-%d %H:%M:%S"),
                description=f.get_description(),
                encoding=f.encoding,
                etag=f.etag,
                flags=f.flags,
                format=f.get_format(),
                full_name=f.get_full_name(),
                full_path=f.get_full_path(),
                hidden=f.hidden,
                license=f.get_license()if hasattr(g, 'get_license') else '',
                magic=f.get_magic(),
                modification_date=f.md.strftime("%Y-%m-%d %H:%M:%S"),
                name=f.get_name(),
                mine=f.mime,
                path=f.get_path(),
                recid=f.get_recid(),
                recids_doctype=f.recids_doctypes,
                size=f.get_size(),
                status=f.get_status(),
                subformat=f.get_subformat(),
                superformat=f.get_superformat(),
                type=f.get_type(),
                url=f.get_url(),
                version=f.get_version(),
            ))

    return bibdocfile_dump
