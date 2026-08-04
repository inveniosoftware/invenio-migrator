# SPDX-FileCopyrightText: 2016 CERN.
# SPDX-License-Identifier: MIT

"""Celery task for records migration."""

from __future__ import absolute_import, print_function

from celery import shared_task

from .utils import load_common


@shared_task()
def load_remoteaccount(data):
    """Load the remote accounts from data dump.

    :param data: Dictionary containing remote accounts data.
    :type data: dict
    """
    from invenio_oauthclient.models import RemoteAccount
    load_common(RemoteAccount, data)


@shared_task()
def load_remotetoken(data):
    """Load the remote tokens from data dump.

    :param data: Dictionary containing remote tokens data.
    :type data: dict
    """
    from invenio_oauthclient.models import RemoteToken
    load_common(RemoteToken, data)


@shared_task()
def load_userext(data):
    """Load the user identities from UserEXT dump.

    :param data: Dictionary containing user identities.
    :type data: dict
    """
    from invenio_oauthclient.models import UserIdentity
    load_common(UserIdentity, data)
