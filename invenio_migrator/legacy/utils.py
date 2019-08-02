# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Helper methods."""

from __future__ import absolute_import, print_function

from functools import wraps
from itertools import islice

from dateutil.tz import tzlocal, tzutc
from pkg_resources import iter_entry_points


def grouper(iterable, n):
    """Create chunks of size `n` from the iterable.

    Example:
    >>> grouper('ABCDEFG', 3)
    ['ABC', 'DEF', 'G']

    """
    it = iter(iterable)
    while True:
        chunk = tuple(islice(it, n))
        if not chunk:
            return
        yield chunk


def collect_things_entry_points():
    """Collect entry points."""
    things = dict()
    for entry_point in iter_entry_points(group='invenio_migrator.things'):
        things[entry_point.name] = entry_point.load()
    return things


def init_app_context():
    """Initialize app context for Invenio 2.x."""
    try:
        from invenio.base.factory import create_app
        app = create_app()
        app.test_request_context('/').push()
        app.preprocess_request()
    except ImportError:
        pass


def datetime_toutc(dt):
    """Convert local datetime to UTC."""
    return dt.replace(tzinfo=tzlocal()).astimezone(tzutc())


def dt2iso_or_empty(dt):
    """Turn datetime object into ISO string (empty if 'dt' is None).

    :param dt: Datetime object
    :type dt: datetime.datetime
    :returns: ISO-formatted date or empty string
    :rtype: str
    """
    return '' if (dt is None) else datetime_toutc(dt).isoformat()


def set_serializer(obj):
    """Turn set into list to serialize it to JSON."""
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


def memoize(func):
    """Cache for heavy function calls."""
    cache = {}

    @wraps(func)
    def wrap(*args, **kwargs):
        key = '{0}{1}'.format(args, kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrap
