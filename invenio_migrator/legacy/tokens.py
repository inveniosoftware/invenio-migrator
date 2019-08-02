# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
