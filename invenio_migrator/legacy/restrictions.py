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
"""Dump of access restrictions (collection, file and record level).

Everything is dumped as stored in the legacy instance: no firerole or status
string is parsed or interpreted.
"""

from __future__ import absolute_import, print_function

from contextlib import contextmanager

from .utils import memoize


def _get_run_sql():
    """Import ``run_sql``."""
    try:
        from invenio.dbquery import run_sql
    except ImportError:
        from invenio.legacy.dbquery import run_sql
    return run_sql


def _get_fieldvalues():
    """Import ``get_fieldvalues``."""
    try:
        from invenio.search_engine_utils import get_fieldvalues
    except ImportError:
        from invenio.legacy.search_engine import get_fieldvalues
    return get_fieldvalues


def _get_grant_tags():
    """Get MARC tags granting owner and viewer rights to a record."""
    try:
        from invenio.access_control_config import (
            CFG_ACC_GRANT_AUTHOR_RIGHTS_TO_EMAILS_IN_TAGS as owner_tags,
            CFG_ACC_GRANT_VIEWER_RIGHTS_TO_EMAILS_IN_TAGS as viewer_tags)
    except ImportError:
        from invenio.modules.access.local_config import (
            CFG_ACC_GRANT_AUTHOR_RIGHTS_TO_EMAILS_IN_TAGS as owner_tags,
            CFG_ACC_GRANT_VIEWER_RIGHTS_TO_EMAILS_IN_TAGS as viewer_tags)
    return list(owner_tags), list(viewer_tags)


@memoize
def _dump_role(row):
    """Dump a role together with its explicit users."""
    run_sql = _get_run_sql()
    role_id, name, description, firerole_def_src = row
    users = [
        dict(email=email,
             expiration=expiration.isoformat() if expiration else None)
        for email, expiration in run_sql(
            'SELECT u.email, ur.expiration FROM user_accROLE AS ur '
            'JOIN user AS u ON u.id=ur.id_user WHERE ur.id_accROLE=%s',
            (role_id, ), run_on_slave=True)
    ]
    return dict(
        id=role_id,
        name=name,
        description=description,
        firerole_def_src=firerole_def_src,
        users=users,
    )


@memoize
def get_action_roles(action, keyword, value):
    """Get roles authorized for ``action`` with argument ``keyword=value``.

    Roles are returned even if they have no explicit users (firerole only).
    """
    run_sql = _get_run_sql()
    rows = run_sql(
        'SELECT DISTINCT r.id, r.name, r.description, r.firerole_def_src '
        'FROM accROLE AS r '
        'JOIN accROLE_accACTION_accARGUMENT AS raa ON r.id=raa.id_accROLE '
        'JOIN accARGUMENT AS a ON a.id=raa.id_accARGUMENT '
        'WHERE raa.id_accACTION=(SELECT id FROM accACTION WHERE name=%s) '
        'AND a.keyword=%s AND a.value=%s ORDER BY r.id',
        (action, keyword, value), run_on_slave=True)
    return [_dump_role(row) for row in rows]


@memoize
def get_action_wildcard_roles(action):
    """Get roles authorized for ``action`` with any argument value.

    These are stored with ``id_accARGUMENT=-1`` and ``argumentlistid=-1``.
    """
    run_sql = _get_run_sql()
    rows = run_sql(
        'SELECT DISTINCT r.id, r.name, r.description, r.firerole_def_src '
        'FROM accROLE AS r '
        'JOIN accROLE_accACTION_accARGUMENT AS raa ON r.id=raa.id_accROLE '
        'WHERE raa.id_accACTION=(SELECT id FROM accACTION WHERE name=%s) '
        'AND raa.id_accARGUMENT=-1 AND raa.argumentlistid=-1 '
        'ORDER BY r.id',
        (action, ), run_on_slave=True)
    return [_dump_role(row) for row in rows]


def dump_collection_restrictions(collections):
    """Dump roles allowed to view each restricted collection."""
    return dict(
        (coll, get_action_roles('viewrestrcoll', 'collection', coll))
        for coll in collections)


def dump_bibdoc_restrictions(recid):
    """Dump the restriction of every restricted BibDoc of a record.

    The status is read straight from the ``bibdoc`` table (same selection as
    ``BibRecDocs(recid).list_bibdocs()``: not deleted), to avoid
    instantiating every BibDoc, which is expensive.
    """
    run_sql = _get_run_sql()
    return [
        dict(bibdocid=bibdocid,
             status=status,
             # Roles granted ``viewrestrdoc`` for this exact status value.
             roles=get_action_roles('viewrestrdoc', 'status', status))
        for bibdocid, status in run_sql(
            'SELECT bd.id, bd.status FROM bibrec_bibdoc AS brbd '
            'JOIN bibdoc AS bd ON bd.id=brbd.id_bibdoc '
            "WHERE brbd.id_bibrec=%s AND bd.status<>'' "
            "AND bd.status<>'DELETED' ORDER BY bd.id",
            (recid, ), run_on_slave=True)
    ]


def dump_record_grants(recid):
    """Dump the values of the MARC tags granting owner/viewer rights."""
    get_fieldvalues = _get_fieldvalues()
    owner_tags, viewer_tags = _get_grant_tags()
    return dict(
        owners=dict((t, get_fieldvalues(recid, t)) for t in owner_tags),
        viewers=dict((t, get_fieldvalues(recid, t)) for t in viewer_tags),
    )


@memoize
def get_edit_collections():
    """Get names of the collections with ``runbibedit`` roles configured."""
    run_sql = _get_run_sql()
    return [row[0] for row in run_sql(
        'SELECT DISTINCT a.value FROM accARGUMENT AS a '
        'JOIN accROLE_accACTION_accARGUMENT AS raa '
        'ON a.id=raa.id_accARGUMENT '
        'WHERE a.keyword="collection" AND raa.id_accACTION='
        '(SELECT id FROM accACTION WHERE name="runbibedit") '
        'ORDER BY a.value', run_on_slave=True)]


def get_collections_in(recid, collections):
    """Get which of the given collections the record belongs to."""
    try:
        from invenio.search_engine import get_collection_reclist
    except ImportError:
        from invenio.legacy.search_engine import get_collection_reclist
    return [coll for coll in collections if recid in get_collection_reclist(
        coll, recreate_cache_if_needed=False)]


@contextmanager
def frozen_collection_cache():
    """Stop legacy from re-validating the collection cache on every call.

    ``get_collection_reclist`` and ``get_all_collections_of_a_record`` (used
    by ``guess_primary_collection_of_a_record`` and ``get_record_status``)
    call ``collection_reclist_cache.recreate_cache_if_needed()`` by default,
    which queries ``information_schema.tables`` each time, i.e. several heavy
    queries per record. The cache is filled once when the legacy module is
    imported, which is good enough for a dump.
    """
    try:
        from invenio.search_engine import collection_reclist_cache
    except ImportError:
        from invenio.legacy.search_engine import collection_reclist_cache

    # Instance attribute shadows the method; removing it restores the class
    # method.
    collection_reclist_cache.recreate_cache_if_needed = lambda: None
    try:
        yield
    finally:
        del collection_reclist_cache.recreate_cache_if_needed


def get_primary_collection(recid):
    """Get the primary collection of a record (used by comment actions)."""
    try:
        from invenio.search_engine import guess_primary_collection_of_a_record
    except ImportError:
        from invenio.legacy.search_engine import (
            guess_primary_collection_of_a_record)
    return guess_primary_collection_of_a_record(recid)


def dump_edit_restrictions(recid):
    """Dump roles allowed to edit the record (``runbibedit`` action).

    The action is granted per collection the record belongs to, or for any
    collection (``any_collection``). Only collections that have ``runbibedit``
    roles configured are listed.
    """
    return dict(
        collections=dict(
            (coll, get_action_roles('runbibedit', 'collection', coll))
            for coll in get_collections_in(recid, get_edit_collections())),
        any_collection=get_action_wildcard_roles('runbibedit'),
    )


def dump_comment_restrictions(recid):
    """Dump comment related restrictions of a record.

    * ``view``/``send``: ``viewcomment``/``sendcomment`` roles, granted per
      primary collection of the record. If the action has no roles at all
      legacy Invenio lets everybody through.
    * ``record_restriction``: the restriction applied to newly submitted
      comments, as set in the record metadata.
    * ``restricted_comments``: restrictions set on existing comments and
      reviews, with the ``viewrestrcomment`` roles that can see them.
    """
    from invenio.webcomment import get_record_status

    run_sql = _get_run_sql()
    with frozen_collection_cache():
        primary_collection = get_primary_collection(recid)
        record_restriction = get_record_status(recid)[0]

    comments = {}
    for comment_id, restriction in run_sql(
            'SELECT id, restriction FROM cmtRECORDCOMMENT '
            'WHERE id_bibrec=%s AND restriction != "" ORDER BY id',
            (recid, ), run_on_slave=True):
        comments.setdefault(restriction, []).append(comment_id)

    return dict(
        primary_collection=primary_collection,
        view=dict(
            roles=get_action_roles(
                'viewcomment', 'collection', primary_collection),
            any_collection=get_action_wildcard_roles('viewcomment')),
        send=dict(
            roles=get_action_roles(
                'sendcomment', 'collection', primary_collection),
            any_collection=get_action_wildcard_roles('sendcomment')),
        record_restriction=record_restriction,
        restricted_comments=[
            dict(restriction=restriction,
                 comment_ids=comment_ids,
                 roles=get_action_roles(
                     'viewrestrcomment', 'status', restriction))
            for restriction, comment_ids in sorted(comments.items())],
    )


def get_restricted_collections(recid):
    """Get names of the restricted collections a record belongs to."""
    try:
        from invenio.search_engine import get_restricted_collections_for_recid
    except ImportError:
        from invenio.legacy.search_engine import (
            get_restricted_collections_for_recid)
    return get_restricted_collections_for_recid(
        recid, recreate_cache_if_needed=False)


def dump_restrictions(recid):
    """Dump all access restrictions that apply to a record.

    :param recid: Record identifier.

    Everything is dumped as stored in legacy, nothing is parsed. Example of
    the output (a ``role`` is ``{id, name, description, firerole_def_src,
    users}``; an empty list means that no role is configured for the action)::

        {
          "collections": {            # viewrestrcoll, restricted colls only
            "ATLAS Internal Notes": [
              {"id": 42, "name": "atlas_internal_viewer",
               "description": "ATLAS members",
               "firerole_def_src": "allow group \"atlas-readaccess\"\n"
                                   "deny any",
               "users": [{"email": "jane.doe@cern.ch", "expiration": null}]}
            ]
          },
          "files": [                  # restricted BibDocs only
            {"bibdocid": 981,
             "status": "restricted_picture",   # raw BibDoc status
             "roles": [...]}                   # viewrestrdoc for that status
          ],
          "record": {                 # MARC tags granting rights (values)
            "owners": {"859__f": ["jane.doe@cern.ch"], "270__m": []},
            "viewers": {"506__m": ["atlas-reviewers"], "5061_d": []}
          },
          "edit": {                   # runbibedit
            "collections": {"ATLAS Internal Notes": [...]},
            "any_collection": [...]   # roles granted with any argument
          },
          "comments": {
            "primary_collection": "ATLAS Internal Notes",
            "view": {"roles": [...], "any_collection": [...]},  # viewcomment
            "send": {"roles": [...], "any_collection": [...]},  # sendcomment
            "record_restriction": "referees",  # applied to new comments
            "restricted_comments": [           # viewrestrcomment
              {"restriction": "referees", "comment_ids": [101, 102],
               "roles": [...]}
            ]
          }
        }

    File statuses with a prefix (``group: x``, ``firerole: ...``, ...) are
    dumped as the raw ``status`` with no ``roles``; interpreting them is left
    to the consumer of the dump.
    """
    return dict(
        collections=dump_collection_restrictions(
            get_restricted_collections(recid)),
        files=dump_bibdoc_restrictions(recid),
        record=dump_record_grants(recid),
        edit=dump_edit_restrictions(recid),
        comments=dump_comment_restrictions(recid),
    )
