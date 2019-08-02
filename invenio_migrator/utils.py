# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
