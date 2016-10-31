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
