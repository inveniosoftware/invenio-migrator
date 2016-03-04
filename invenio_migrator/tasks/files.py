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

"""Celery task for files migration."""

from __future__ import absolute_import, print_function

import arrow
from celery import shared_task
from flask import current_app
from invenio_db import db
from invenio_files_rest.models import FileInstance, ObjectVersion


def make_checksum_str(checksum):
    """Make a checksum."""
    return "md5:{0}".format(checksum)


@shared_task(ignore_result=True)
def create_file(bucket_id, key, file_versions):
    """Create a file in a bucket including all versions.

    :param bucket_id: Bucket to create file in.
    :param key: Key of file in bucket.
    :param file_versions: List of dictionaries with each dictionary
        representing a file version. List must be order from oldest to newest.
        The dictionary must have the following keys: ``uri``, ``size``,
        ``checksum``,  ``created``.
    """
    try:
        objs = []
        for v in file_versions:
            f = FileInstance.get_or_create(
                v['uri'],
                storage_class=v.get('storage_class'),
                size=v['size'],
                checksum=make_checksum_str(v['checksum']),
                read_only=True,
            )
            obj = ObjectVersion(
                bucket_id=bucket_id,
                key=key,
                is_head=False,
                file_id=f.id,
                created=arrow.get(v['created']).datetime,
            )
            db.session.add(obj)
            objs.append(obj)

        # Assert version ordering of objects.
        prev_o = objs[0]
        for o in objs[1:]:
            assert prev_o.created <= o.created

        # Set head version
        objs[-1].is_head = True

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    # Send post tasks.
    current_app.extensions['invenio-migrator'].files_post_task_factory(
        bucket_id,
        key
    )
