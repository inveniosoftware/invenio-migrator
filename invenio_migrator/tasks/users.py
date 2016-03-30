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
from invenio_accounts.models import User
from invenio_db import db


@shared_task()
def load_user(data):
    """Load user from data dump.

    :param data: Dictionary containing user data.
    :type data: dict
    """
    email = data['email']
    if User.query.filter_by(email=data['email']).count() > 0:
        email = 'DUPLICATE_{}'.format(data['email'])
    obj = User(
        id=data['id'],
        email=email)
    db.session.add(obj)
    db.session.commit()
