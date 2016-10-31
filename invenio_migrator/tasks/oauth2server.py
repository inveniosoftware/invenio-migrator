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

"""Celery task for oauth2server migration."""

from __future__ import absolute_import, print_function

from celery import shared_task

from .utils import iso2dt_or_none, load_common


@shared_task()
def load_client(data):
    """Load the oauth2server client from data dump."""
    from invenio_oauth2server.models import Client
    load_common(Client, data)


@shared_task()
def load_token(data):
    """Load the oauth2server token from data dump."""
    from invenio_oauth2server.models import Token
    data['expires'] = iso2dt_or_none(data['expires'])
    load_common(Token, data)
