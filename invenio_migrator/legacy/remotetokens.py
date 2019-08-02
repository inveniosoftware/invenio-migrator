# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Remote token dump functions."""

from __future__ import absolute_import, print_function


def get(*args, **kwargs):
    """Get users."""
    from invenio.modules.oauthclient.models import RemoteToken
    q = RemoteToken.query
    return q.count(), q.all()


def dump(rt, from_date, with_json=True, latest_only=False, **kwargs):
    """Dump the remote tokens as a list of dictionaries.

    :param ra: Remote toekn to be dumped.
    :type ra: `invenio_oauthclient.models.RemoteToken [Invenio2.x]`
    :returns: Remote tokens serialized to dictionary.
    :rtype: dict
    """
    return dict(id_remote_account=rt.id_remote_account,
                token_type=rt.token_type,
                access_token=rt.access_token,
                secret=rt.secret)
