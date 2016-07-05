# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Celery task for remote account migration."""

from __future__ import absolute_import, print_function

from celery import shared_task

from invenio_db import db
from invenio_oauthclient.models import RemoteAccount
from invenio_oauthclient.models import UserIdentity


@shared_task()
def load_remoteacount(data):
    """Load remoteaccount from data dump.

    :param data: Dictionary containing user data.
    :type data: dict
    """
    with db.session.begin_nested():
        remoteaccount = data['remoteaccount']
        if remoteaccount:
            obj = RemoteAccount(
                id=remoteaccount['id'],
                user_id=remoteaccount['user_id'],
                client_id=remoteaccount['client_id'],
                extra_data=remoteaccount['extra_data']
            )
            db.session.add(obj)

        userext = data['userext']
        if userext:
            obj = UserIdentity(
                id=userext['id'],
                method=userext['method'],
                id_user=userext['id_user']
            )
            db.session.add(obj)

    db.session.commit()
