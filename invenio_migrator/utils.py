# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
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

"""Utility methods and classes to ease the migration process."""


from functools import wraps

from invenio_records.models import Timestamp, timestamp_before_update
from sqlalchemy.event import contains, listen, remove


class correct_date(object):
    """Temporarily disable Timestamp date update."""

    def __enter__(self):
        """Disable date update."""
        self._found = contains(
            Timestamp, 'before_update', timestamp_before_update)
        if self._found:
            remove(Timestamp, 'before_update', timestamp_before_update)

    def __exit__(self, type, value, traceback):
        """Re-enable date update."""
        if self._found:
            listen(Timestamp, 'before_update', timestamp_before_update)


def disable_timestamp(method):
    """Disable timestamp update per method."""
    @wraps(method)
    def wrapper(*args, **kwargs):
        result = None
        with correct_date():
            result = method(*args, **kwargs)
        return result
    return wrapper
