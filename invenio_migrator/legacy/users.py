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

"""Community dump functions."""

from __future__ import absolute_import, print_function

from .utils import dt2iso_or_empty


def get(*args, **kwargs):
    """Get users."""
    from invenio.modules.accounts.models import User
    q = User.query
    return q.count(), q.all()


def dump(u, from_date, with_json=True, latest_only=False, **kwargs):
    """Dump the users as a list of dictionaries.

    TODO: This is only dumping user info without passwords.

    :param u: User to be dumped.
    :type u: `invenio_accounts.models.User [Invenio2.x]`
    :returns: User serialized to dictionary.
    :rtype: dict
    """
    return dict(id=u.id,
                email=u.email,
                note=u.note,
                given_names=u.given_names,
                family_name=u.family_name,
                settings=u.settings,
                nickname=u.nickname,
                last_login=dt2iso_or_empty(u.last_login))
