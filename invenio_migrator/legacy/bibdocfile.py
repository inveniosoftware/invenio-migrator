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

"""Bibdocfile metadata dumper."""

from __future__ import absolute_import, print_function

import datetime

import click

from .utils import datetime_toutc


def _get_recids_invenio12(from_date):
    """Get BibDocs for Invenio 1."""
    from invenio.dbquery import run_sql
    return (id[0] for id in run_sql(
        'select id_bibrec from '
        'bibrec_bibdoc as r join bibdoc as d on r.id_bibdoc=d.id '
        'where d.modification_date >=%s',
        (from_date, ), run_on_slave=True))


def _get_recids_invenio2(from_date):
    """Get BibDocs for Invenio 2."""
    from invenio.legacy.dbquery import run_sql
    return (id[0] for id in run_sql(
        'select id_bibrec from '
        'bibrec_bibdoc as r join bibdoc as d on r.id_bibdoc=d.id '
        'where d.modification_date >=%s',
        (from_date, ), run_on_slave=True))


def get_modified_bibdoc_recids(from_date):
    """Get bibdocs."""
    try:
        return set(_get_recids_invenio12(from_date))
    except ImportError:
        return set(_get_recids_invenio2(from_date))


def _import_bibdoc():
    """Import BibDocFile."""
    try:
        from invenio.bibdocfile import BibRecDocs, BibDoc
    except ImportError:
        from invenio.legacy.bibdocfile.api import BibRecDocs, BibDoc
    return BibRecDocs, BibDoc


def dump_bibdoc(recid, from_date, **kwargs):
    """Dump all BibDoc metadata.

    :param docid: BibDoc ID
    :param from_date: Dump only BibDoc revisions newer than this date.

    :returns: List of version of the BibDoc formatted as a dict
    """
    BibRecDocs, BibDoc = _import_bibdoc()

    bibdocfile_dump = []

    date = datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')
    for bibdoc in BibRecDocs(recid).list_bibdocs():
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
                    copyright=(
                        f.get_copyright() if hasattr(f, 'get_copyright')
                        else None),
                    creation_date=datetime_toutc(f.cd).isoformat(),
                    description=f.get_description(),
                    encoding=f.encoding,
                    etag=f.etag,
                    flags=f.flags,
                    format=f.get_format(),
                    full_name=f.get_full_name(),
                    full_path=f.get_full_path(),
                    hidden=f.hidden,
                    license=(
                        f.get_license()if hasattr(f, 'get_license') else None),
                    modification_date=datetime_toutc(f.md).isoformat(),
                    name=f.get_name(),
                    mime=f.mime,
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


def get_check():
    """Get bibdocs to check."""
    try:
        from invenio.dbquery import run_sql
    except ImportError:
        from invenio.legacy.dbquery import run_sql

    return (
        run_sql('select count(id) from bibdoc', run_on_slave=True)[0][0],
        [id[0] for id in run_sql('select id from bibdoc', run_on_slave=True)],
    )


def check(id_):
    """Check bibdocs."""
    BibRecDocs, BibDoc = _import_bibdoc()

    try:
        BibDoc(id_).list_all_files()
    except Exception:
        click.secho("BibDoc {0} failed check.".format(id_), fg='red')
