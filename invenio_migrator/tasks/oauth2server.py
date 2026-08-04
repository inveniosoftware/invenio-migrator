# SPDX-FileCopyrightText: 2016 CERN.
# SPDX-License-Identifier: MIT

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
