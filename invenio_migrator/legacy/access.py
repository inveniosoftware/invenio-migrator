# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016, 2017 CERN.
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

"""Access rights dump functions."""

from __future__ import absolute_import, print_function

import six


def _get_run_sql():
    """Import ``run_sql``."""
    try:
        from invenio.dbquery import run_sql
    except ImportError:
        from invenio.legacy.dbquery import run_sql
    return run_sql


def get_connected_roles(action_id):
    """Get roles connected to an action."""
    try:
        from invenio.access_control_admin import compile_role_definition
    except ImportError:
        from invenio.modules.access.firerole import compile_role_definition

    run_sql = _get_run_sql()

    roles = {}
    res = run_sql(
        'select r.id, r.name, r.description, r.firerole_def_src, '
        'a.keyword, a.value, email from accROLE as r '
        'join accROLE_accACTION_accARGUMENT on r.id=id_accROLE '
        'join accARGUMENT as a on  a.id=id_accARGUMENT '
        'join user_accROLE as u on r.id=u.id_accROLE '
        'join user on user.id=u.id_user '
        'where id_accACTION=%s', (action_id, )
    )

    for r in res:
        role = roles.setdefault(
            r[0], {
                'id': r[0],
                'name': r[1],
                'description': r[2],
                'firerole_def': r[3],
                'compiled_firerole_def': compile_role_definition(r[3]),
                'users': set(),
                'parameters': {}
            }
        )
        param = role['parameters'].setdefault(r[4], set())
        param.add(r[5])
        role['users'].add(r[6])

    return six.itervalues(roles)


def get(query, *args, **kwargs):
    """Get action definitions to dump."""
    run_sql = _get_run_sql()

    actions = [
        dict(id=row[0],
             name=row[1],
             allowedkeywords=row[2],
             optional=row[3])
        for action in query.split(',') for row in run_sql(
            'select id, name, description, allowedkeywords, optional '
            'from accACTION where name like %s', (action, ),
            run_on_slave=True)
    ]

    return len(actions), actions


def dump(action, *args, **kwargs):
    """Dump all roles connected with the action."""
    action['roles'] = list(get_connected_roles(action['id']))
    return action
