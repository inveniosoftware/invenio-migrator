# -*- coding: utf-8 -*-

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

""""Helper methods."""

from __future__ import absolute_import, print_function

from dateutil.parser import parse as iso2dt


def iso2dt_or_none(iso_dt):
    """Turn ISO-formatted date into datetime (None if 'iso_dt' is empty).

    :param iso_dt: ISO-formatted date
    :type iso_dt: str
    :returns: datetime object or None
    :rtype: datetime
    """
    return iso2dt(iso_dt) if iso_dt else None


def logo_ext_wash(logo_ext):
    """Handle the legacy logo extensions.

    Examples:
    None -> None
    'png' -> 'png'
    '0' -> None
    '.jpg' -> 'jpg'

    :param logo_ext: Community logo extension.
    :type logo_ext: string or None
    :returns: Washed logo extension.
    :rtype: string or None
    """
    if logo_ext is None:
        return None
    elif logo_ext == '0':
        return None
    elif logo_ext.startswith('.'):
        return logo_ext[1:]
    else:
        return logo_ext
