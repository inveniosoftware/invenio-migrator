# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Remote account dump functions."""

from __future__ import absolute_import, print_function


def get(*args, **kwargs):
    """Get users."""
    from invenio.modules.oauthclient.models import RemoteAccount
    q = RemoteAccount.query
    return q.count(), q.all()


def dump(ra, from_date, with_json=True, latest_only=False, **kwargs):
    """Dump the remote accounts as a list of dictionaries.

    :param ra: Remote account to be dumped.
    :type ra: `invenio_oauthclient.models.RemoteAccount [Invenio2.x]`
    :returns: Remote accounts serialized to dictionary.
    :rtype: dict
    """
    return dict(id=ra.id, user_id=ra.user_id, client_id=ra.client_id,
                extra_data=ra.extra_data)
