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

from datetime import datetime

import arrow
from celery import shared_task
from flask import current_app
from invenio_db import db

from .errors import UserEmailExistsError, UserUsernameExistsError


@shared_task()
def load_user(data):
    """Load user from data dump.

    NOTE: This task takes into account the possible duplication of emails and
    usernames, hence it should be called synchronously.
    In such case of collision it will raise UserEmailExistsError or
    UserUsernameExistsError, if email or username are already existing in
    the database. Caller of this task should take care to to resolve those
    collisions beforehand or after catching an exception.

    :param data: Dictionary containing user data.
    :type data: dict
    """
    from invenio_accounts.models import User
    from invenio_userprofiles.api import UserProfile
    email = data['email'].strip()
    if User.query.filter_by(email=email).count() > 0:
        raise UserEmailExistsError(
            "User email '{email}' already exists.".format(email=email))

    last_login = None
    if data['last_login']:
        last_login = arrow.get(data['last_login']).datetime

    confirmed_at = None
    if data['note'] == '1':
        confirmed_at = datetime.utcnow()

    salt = data['password_salt']
    checksum = data['password']
    if not checksum:
        new_password = None
    # Test if password hash is in Modular Crypt Format
    elif checksum.startswith('$'):
        new_password = checksum
    else:
        new_password = str.join('$', ['', u'invenio-aes', salt, checksum])
    with db.session.begin_nested():
        obj = User(
            id=data['id'],
            password=new_password,
            email=email,
            confirmed_at=confirmed_at,
            last_login_at=last_login,
            active=(data['note'] != '0'),
        )
        db.session.add(obj)

    nickname = data['nickname'].strip()
    overwritten_username = ('username' in data and 'displayname' in data)
    # NOTE: 'username' and 'displayname' will exist in data dump only
    # if it was inserted there after dumping. It normally should not come from
    # Invenio 1.x or 2.x data dumper script. In such case, those values will
    # have precedence over the 'nickname' field.
    if nickname or overwritten_username:
        full_name = (data.get('given_names', '') + u' ' +
                     data.get('family_name', '')).strip()

        p = UserProfile(user=obj)
        p.full_name = full_name or ''
        if overwritten_username:
            p._username = data['username'].lower()
            p._displayname = data['displayname']
        elif nickname:
            if UserProfile.query.filter(
                    UserProfile._username == nickname.lower()).count() > 0:
                raise UserUsernameExistsError(
                    "Username '{username}' already exists.".format(
                        username=nickname))
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
