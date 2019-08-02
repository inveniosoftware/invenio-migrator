# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community dump functions."""

from __future__ import absolute_import, print_function


def get(*args, **kwargs):
    """Get UserEXT objects."""
    try:
        from invenio.modules.accounts.models import UserEXT
    except ImportError:
        from invenio_accounts.models import UserEXT
    q = UserEXT.query
    return q.count(), q.all()


def dump(u, from_date, with_json=True, latest_only=False, **kwargs):
    """Dump the UserEXt objects as a list of dictionaries.

    :param u: UserEXT to be dumped.
    :type u: `invenio_accounts.models.UserEXT [Invenio2.x]`
    :returns: User serialized to dictionary.
    :rtype: dict
    """
    return dict(id=u.id, method=u.method, id_user=u.id_user)
