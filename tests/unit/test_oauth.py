# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
