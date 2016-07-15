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

"""Invenio OAuth2Server Token dump functions."""

from __future__ import absolute_import, print_function

from .utils import dt2iso_or_empty


def get(*args, **kwargs):
    """Get users."""
    from invenio.modules.oauth2server.models import Token
    q = Token.query
    return q.count(), q.all()


def dump(obj, from_date, with_json=True, latest_only=False, **kwargs):
    """Dump the oauth2server tokens."""
    return dict(id=obj.id,
                client_id=obj.client_id,
                user_id=obj.user_id,
                token_type=obj.token_type,
                access_token=obj.access_token,
                refresh_token=obj.refresh_token,
                expires=dt2iso_or_empty(obj.expires),
                _scopes=obj._scopes,
                is_personal=obj.is_personal,
                is_internal=obj.is_internal)
