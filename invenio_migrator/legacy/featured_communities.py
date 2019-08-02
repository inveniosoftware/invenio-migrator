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
    """Get communities."""
    from invenio.modules.communities.models import FeaturedCommunity
    q = FeaturedCommunity.query
    return q.count(), q.all()


def dump(fc, from_date, with_json=True, latest_only=False, **kwargs):
    """Dump the community object as dictionary.

    :param fc: Community featuring to be dumped.
    :type fc: `invenio_communities.models.FeaturedCommunity [Invenio2.x]`
    :returns: Community serialized to dictionary.
    :rtype: dict
    """
    return dict(id=fc.id,
                id_community=fc.id_community,
                start_date=fc.start_date.isoformat())
