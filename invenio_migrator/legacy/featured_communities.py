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
