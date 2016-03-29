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

"""Community records."""

from __future__ import absolute_import, print_function


def iso_or_none(date_):
    """Helper."""
    return '' if (date_ is None) else date_.isoformat()


def get(query, from_date, **kwargs):
    """Get recids matching query and with changes."""
    from invenio.modules.communities.models import Community, FeaturedCommunity

    total = Community.query.count() + FeaturedCommunity.query.count()

    communities = Community.query.all()
    communities.extend(FeaturedCommunity.query.all())

    return total, communities


def dump(u, from_date, **kwargs):
    """Dump JSON representation of a community.

    :param community_id: Record identifier
    :param from_date: Dump only revisions from this date onwards.
    :param json_converter: Function to convert the record to JSON
    :returns: List of versions of the record.
    """
    # TODO: Dump logo files!!
    from invenio.modules.communities.models import Community, FeaturedCommunity
    data = dict(community=None, featured=None)

    if isinstance(u, Community):
        data['community'] = dict(
            id=u.id,
            id_user=u.id_user,
            id_collection=u.id_collection,
            id_collection_provisional=u.id_collection_provisional,
            id_oairepository=u.id_oairepository,
            title=u.title,
            description=u.description,
            page=u.page,
            curation_policy=u.curation_policy,
            logo_ext=u.logo_ext,
            created=u.created.isoformat(),
            last_modified=u.last_modified.isoformat(),
            last_record_accepted=iso_or_none(u.last_record_accepted),
            ranking=u.ranking,
            fixed_points=u.fixed_points,
        )
    elif isinstance(u, FeaturedCommunity):
        data['featured'] = dict(
            id=u.id,
            id_community=u.id_community,
            start_date=u.start_date.isoformat(),
         )
    return data
