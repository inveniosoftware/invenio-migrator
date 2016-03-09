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

"""Record migration loading tasks."""

from __future__ import absolute_import, print_function

from celery import shared_task
from flask import current_app
from invenio_db import db
from invenio_records.api import Record
from invenio_pidstore.resolver import Resolver
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus


@shared_task(ignore_resul=True)
def create_record_revisions(record_revisions):
    """Create/Update record and mint PIDs."""
    # if not record_revisions:
    #     return

    pid_key = current_app.config.get('MIGRATOR_RECORDS_MIGRATION_PID')

    pid_value = record_revisions[0].get(main_pid_key, None)
    assert pid_value

    resolver = Resolver(pid_type='recid', object_type='rec',
                        getter=Record.get_record)
    try:
        id_, record = resolver.resolve(pid_value)
    except PIDDoesNotExistError:
        id_, record = (None, None)

    for revision in record_revisions:
        if record is None:
            record = Record.create(revision)
            id_ = record.id
        else:
            record.model.json = revision
            record = record.commit()
        pid_status = pid_legacy_status(record)
        if pid_status == PIDStatus.DELETE:
            record.delete()

        for fetcher in current_app.extensions[
                'invenio-migrator'].records_pid_fetchers:
            fetched_pid = fetcher(id_, record)
            pid = PersistentIdentifier.get(*fetched_pid)
            if not pid:
                pid = PersistentIdentifier.create(
                    pid_type=fetched_pid.pid_type,
                    pid_value=fetched_pid.pid_value,
                    object_type='rec',
                    object_uuid=str(id_),
                    status=pid_status
                )
            elif pid_status == PIDStatus.DELETE:
                pid.delete()

    current_app.extensions['invenio-migrator'].files_post_task_factory(id_)

    return str(id_)


def pid_legacy_status(data):
    """Extract PID status."""
    if any(col.get('deleted') for col in data.get('collections', [])):
        return PIDStatus.DELETED
    return PIDStatus.REGISTERED
