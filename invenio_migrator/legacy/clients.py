# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio OAuth2Server Client dump functions."""

from __future__ import absolute_import, print_function


def get(*args, **kwargs):
    """Get users."""
    from invenio.modules.oauth2server.models import Client
    q = Client.query
    return q.count(), q.all()


def dump(obj, from_date, with_json=True, latest_only=False, **kwargs):
    """Dump the oauth2server Client."""
    return dict(name=obj.name,
                description=obj.description,
                website=obj.website,
                user_id=obj.user_id,
                client_id=obj.client_id,
                client_secret=obj.client_secret,
                is_confidential=obj.is_confidential,
                is_internal=obj.is_internal,
                _redirect_uris=obj._redirect_uris,
                _default_scopes=obj._default_scopes)
