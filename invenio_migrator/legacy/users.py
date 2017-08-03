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
"""Community dump functions."""

from __future__ import absolute_import, print_function

from collections import namedtuple
from .utils import dt2iso_or_empty


def _get_users_invenio12(*args, **kwargs):
    """Get user accounts Invenio 1."""
    from invenio.dbquery import run_sql, deserialize_via_marshal
    User = namedtuple('User', [
        'id', 'email', 'password', 'password_salt', 'note', 'full_name',
        'settings', 'nickname', 'last_login'
    ])
    users = run_sql(
        'SELECT id, email, password, note, settings, nickname, last_login'
        ' FROM user',
        run_on_slave=True)
    return len(users), [
        User(
            id=user[0],
            email=user[1],
            password=user[2].decode('latin1'),
            password_salt=user[1],
            note=user[3],
            full_name=user[5],
            settings=deserialize_via_marshal(user[4]) if user[4] else {},
            # we don't have proper nicknames on Invenio v1
            nickname='id_{0}'.format(user[0]),
            last_login=user[6]) for user in users
    ]


def _get_users_invenio2(*args, **kwargs):
    """Get user accounts from Invenio 2."""
    from invenio.modules.accounts.models import User
    q = User.query
    return q.count(), q.all()


def get(*args, **kwargs):
    """Get users."""
    try:
        return _get_users_invenio12(*args, **kwargs)
    except ImportError:
        return _get_users_invenio2(*args, **kwargs)


def dump(u, *args, **kwargs):
    """Dump the users as a list of dictionaries.

    :param u: User to be dumped.
    :type u: `invenio.modules.accounts.models.User [Invenio2.x]` or namedtuple.
    :returns: User serialized to dictionary.
    :rtype: dict
    """
    return dict(
        id=u.id,
        email=u.email,
        password=u.password,
        password_salt=u.password_salt,
        note=u.note,
        full_name=u.full_name if hasattr(u, 'full_name') else '{0} {1}'.format(
            u.given_names, u.family_name),
        settings=u.settings,
        nickname=u.nickname,
        last_login=dt2iso_or_empty(u.last_login))
