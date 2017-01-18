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

"""Circulation Locations dump functions."""


def get(query=None, from_date='1970-01-01 00:00:00', only_used=False, **kwargs):
    """Get locations.

    :param query: unused
    :param from_date: unsed
    :param only_used: If set to ``True`` only return used location in the
        ``crcITEM`` table.

    :returns: List of dictionaries containing the locations stored in the DB.
        There is no need to do a two step process as the ``crcLIBRARY`` table
        is isolated from the others in the circulation module.
    :rtype: list
    """
    try:
        from invenio.dbquery import run_sql
    except ImportError:
        from invenio.legacy.dbquery import run_sql

    query = 'SELECT id, name, address, email, phone, type, notes FROM crcLIBRARY'
    if only_used:
        query += ' WHERE id IN (SELECT DISTINCT(id_crcLIBRARY) FROM crcITEM)'

    res = [dict(id=location[0],
                 name=location[1],
                 address=location[2],
                 email=location[3],
                 phone=location[4],
                 type=location[5],
                 notes=location[6])
            for location in run_sql(query, run_on_slave=True)]
    return len(res), res


def dump(location, *args, **kwargs):
    """Return the location itself as it was properly built already.

    :param location: Location to be dumped.
    """
    return location
