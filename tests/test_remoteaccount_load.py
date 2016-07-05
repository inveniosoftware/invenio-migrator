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

"""Test remote account loading."""

from __future__ import absolute_import, print_function

from invenio_oauthclient.models import RemoteAccount, UserIdentity

from invenio_migrator.tasks.remoteaccount import load_remoteacount


def test_deposit_load_task(db, remoteaccount_users, remoteaccount_json):
    """Test the remoteaccount loading task."""
    for remoteaccount in remoteaccount_json:
        load_remoteacount.delay(remoteaccount)

    assert RemoteAccount.query.count() == 2

    remoteaccount1, remoteaccount2 = RemoteAccount.query.all()
    assert remoteaccount1.user_id == 1
    assert remoteaccount1.client_id == u'0000-0000-0000-0000'
    assert remoteaccount1.extra_data == {u'orcid': u'0000-0001-9999-9999'}
    assert remoteaccount2.user_id == 2
    assert remoteaccount2.client_id == u'0000-0000-0000-0000'
    assert remoteaccount2.extra_data == {u'orcid': u'0000-0002-XXXX-YYYY'}

    assert UserIdentity.query.count() == 1

    useridentity = UserIdentity.query.one()
    assert useridentity.id == u'0000-0002-XXXX-YYYY'
    assert useridentity.method == u'orcid'
    assert useridentity.id_user == 2
