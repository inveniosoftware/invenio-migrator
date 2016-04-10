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

import uuid
from datetime import datetime

import arrow
from celery import shared_task
from flask import current_app
from invenio_accounts.models import User
from invenio_db import db
from invenio_userprofiles.api import UserProfile


@shared_task()
def load_user(data):
    """Load user from data dump.

    :param data: Dictionary containing user data.
    :type data: dict
    """
    email = data['email']
    if User.query.filter_by(email=data['email']).count() > 0:
        email = 'DUPLICATE_{}'.format(data['email'])

    last_login = None
    if data['last_login']:
        last_login = arrow.get(data['last_login']).datetime

    confirmed_at = None
    if data['note'] == '1':
        confirmed_at = datetime.utcnow()

    with db.session.begin_nested():
        obj = User(
            id=data['id'],
            password=None,
            email=email,
            confirmed_at=confirmed_at,
            last_login_at=last_login,
            active=(data['note'] != '0'),
        )
        db.session.add(obj)

    nickname = data['nickname'].strip()
    if nickname:
        full_name = (data.get('given_names', '') + u' ' +
                     data.get('family_name', '')).strip()

        if UserProfile.query.filter(
                UserProfile._username == nickname.lower()).count() > 0:
            nickname = 'DUPLICATE_{0}_{1}'.format(str(uuid.uuid4()), nickname)

        p = UserProfile(user=obj)
        p.full_name = full_name or ''
        try:
            p.username = nickname
        except ValueError:
            current_app.logger.warn(
                u'Invalid username {0} for user_id {1}'.format(
                    nickname, data['id']))
            p._username = nickname.lower()
            p._displayname = nickname

        db.session.add(p)

    db.session.commit()
