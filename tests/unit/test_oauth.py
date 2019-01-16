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

"""Module tests."""

from __future__ import absolute_import, print_function

from invenio_migrator.tasks.oauth2server import load_client, load_token
from invenio_migrator.tasks.oauthclient import load_remoteaccount, \
    load_remotetoken


def test_oauthclient_load(dummy_location, oauthclient_dump, deposit_user, app):
    """Test the deposit loading function."""
    remoteaccounts, remotetokens = oauthclient_dump
    for ra in remoteaccounts:
        load_remoteaccount(ra)
    for rt in remotetokens:
        load_remotetoken(rt)


def test_oauth2server_load(dummy_location, oauth2server_dump, deposit_user,
                           app):
    """Test the deposit loading function."""
    clients, tokens = oauth2server_dump
    for client in clients:
        load_client(client)
    for token in tokens:
        load_token(token)
