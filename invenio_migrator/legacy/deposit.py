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

"""Invenio-Deposit migration."""

from __future__ import absolute_import, print_function

import datetime
import json
from itertools import islice

from .utils import datetime_toutc


def dt2utc_timestamp(dt):
    """Serialize the datetime to UTC timestamp."""
    return datetime_toutc(dt).isoformat()


def default_serializer(o):
    """Default serializer for json."""
    defs = (
        ((datetime.date, datetime.time),
         lambda x: x.isoformat(), ),
        ((datetime.datetime, ),
         lambda x: dt2utc_timestamp(x), ),
    )
    for types, fun in defs:
        if isinstance(o, types):
            return fun(o)


def get(query, from_date, limit=0, **kwargs):
    """Get deposits."""
    from invenio.modules.deposit.models import Deposition
    dep_generator = Deposition.get_depositions()
    total_depids = 1  # Count of depositions is hard to determine

    # If limit provided, serve only first n=limit items
    if limit > 0:
        dep_generator = islice(dep_generator, limit)
        total_depids = limit
    return total_depids, dep_generator


def dump(deposition, from_date, with_json=True, latest_only=False, **kwargs):
    """Dump the deposition object as dictionary."""
    # Serialize the __getstate__ and fall back to default serializer
    dep_json = json.dumps(deposition.__getstate__(),
                          default=default_serializer)
    dep_dict = json.loads(dep_json)
    dep_dict['_p'] = {}
    dep_dict['_p']['id'] = deposition.id
    dep_dict['_p']['created'] = dt2utc_timestamp(deposition.created)
    dep_dict['_p']['modified'] = dt2utc_timestamp(deposition.modified)
    dep_dict['_p']['user_id'] = deposition.user_id
    dep_dict['_p']['state'] = deposition.state
    dep_dict['_p']['has_sip'] = deposition.has_sip()
    dep_dict['_p']['submitted'] = deposition.submitted
    return dep_dict
