# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Helper methods."""

from __future__ import absolute_import, print_function

from dateutil.parser import parse as iso2dt
from invenio_db import db


def load_common(model_cls, data):
    """Helper function for loading JSON data verbatim into model."""
    obj = model_cls(**data)
    db.session.add(obj)
    db.session.commit()


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

    :param logo_ext: Community logo extension.
    :type logo_ext: string or None
    :returns: Washed logo extension.
    :rtype: string or None

    Examples:
      None -> None
      'png' -> 'png'
      '0' -> None
      '.jpg' -> 'jpg'

    """
    if logo_ext is None:
        return None
    elif logo_ext == '0':
        return None
    elif logo_ext.startswith('.'):
        return logo_ext[1:]
    else:
        return logo_ext


def empty_str_if_none(value):
    """Convert None to empty strings."""
    return "" if value is None else value
