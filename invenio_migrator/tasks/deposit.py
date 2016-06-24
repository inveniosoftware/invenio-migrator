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
from celery.utils.log import get_task_logger

from .errors import DepositMultipleRecids, DepositRecidDoesNotExist, \
    DepositSIPUserDoesNotExist

logger = get_task_logger(__name__)


@shared_task()
def load_deposit(data):
    """Load the raw JSON dump of the Deposition.

    Uses Record API in order to bypass all Deposit-specific initialization,
    which are to be done after the final stage of deposit migration.

    :param data: Dictionary containing deposition data.
    :type data: dict
    """
    from invenio_db import db
    deposit, dep_pid = create_record_and_pid(data)
    deposit = create_files_and_sip(deposit, dep_pid)
    db.session.commit()


def create_record_and_pid(data):
    """Create the deposit record metadata and persistent identifier.

    :param data: Raw JSON dump of the deposit.
    :type data: dict
    :returns: A deposit object and its pid
    :rtype: (`invenio_records.api.Record`,
             `invenio_pidstore.models.PersistentIdentifier`)
    """
    from invenio_records.api import Record
    from invenio_pidstore.models import PersistentIdentifier, PIDStatus

    deposit = Record.create(data=data)
    depid = deposit['_p']['id']
    pid = PersistentIdentifier.create(
        pid_type='depid',
        pid_value=str(depid),
        object_type='rec',
        object_uuid=str(deposit.id),
        status=PIDStatus.REGISTERED
    )
    deposit.commit()
    return deposit, pid


def create_files_and_sip(deposit, dep_pid):
    """Create deposit Bucket, Files and SIPs."""
    from invenio_pidstore.errors import PIDDoesNotExistError
    from invenio_pidstore.models import PersistentIdentifier
    from invenio_sipstore.errors import SIPUserDoesNotExist
    from invenio_sipstore.models import SIP, RecordSIP, SIPFile
    from invenio_files_rest.models import Bucket, FileInstance, ObjectVersion
    from invenio_records_files.models import RecordsBuckets
    from invenio_db import db
    buc = Bucket.create()
    recbuc = RecordsBuckets(record_id=deposit.id, bucket_id=buc.id)
    db.session.add(recbuc)
    deposit.setdefault('_deposit', dict())
    deposit.setdefault('_files', list())
    files = deposit.get('files', [])
    sips = deposit.get('sips', [])
    recid = None

    if sips:
        recids = [int(sip['metadata']['recid']) for sip in sips]
        if len(set(recids)) > 1:
            logger.error('Multiple recids ({recids}) found in deposit {depid}'
                         ' does not exists.'.format(recids=recids,
                                                    depid=dep_pid.pid_value))
            raise DepositMultipleRecids(dep_pid.pid_value, list(set(recids)))
        elif recids:  # If only one recid
            recid = recids[0]

    # Store the path -> FileInstance mappings for SIPFile creation later
    dep_file_instances = list()

    for file_ in files:
        fi = FileInstance.create()
        fi.set_uri(file_['path'], file_['size'], file_['checksum'])
        ov = ObjectVersion.create(buc, file_['name'], _file_id=fi.id)
        file_meta = dict(
            bucket=str(buc.id),
            key=file_['name'],
            checksum=file_['checksum'],
            size=file_['size'],
            version_id=str(ov.version_id),
        )
        deposit['_files'].append(file_meta)
        dep_file_instances.append((file_['path'], fi))

    for idx, sip in enumerate(sips):
        agent = None
        user_id = None
        if sip['agents']:
            agent = dict(
                ip_address=sip['agents'][0].get('ip_address', ""),
                email=sip['agents'][0].get('email_address', ""),
            )
            user_id = sip['agents'][0]['user_id']
        content = sip['package']
        sip_format = 'marcxml'
        try:
            sip = SIP.create(sip_format,
                             content,
                             user_id=user_id,
                             agent=agent)
        except SIPUserDoesNotExist:
            logger.exception('User ID {user_id} referred in deposit {depid} '
                             'does not exists.'.format(
                                 user_id=user_id, depid=dep_pid.pid_value))
            raise DepositSIPUserDoesNotExist(dep_pid.pid_value, user_id)

        # If recid was found, attach it to SIP
        # TODO: This is always uses the first recid, as we quit if multiple
        # recids are found in the sips information
        if recid:
            try:
                pid = PersistentIdentifier.get(pid_type='recid',
                                               pid_value=recid)
                record_sip = RecordSIP(sip_id=sip.id, pid_id=pid.id)
                db.session.add(record_sip)
            except PIDDoesNotExistError:
                logger.exception('Record {recid} referred in '
                                 'Deposit {depid} does not exists.'.format(
                                     recid=recid, depid=dep_pid.pid_value))
                raise DepositRecidDoesNotExist(dep_pid.pid_value, recid)
        if idx == 0:
            for fp, fi in dep_file_instances:
                sipf = SIPFile(sip_id=sip.id, filepath=fp, file_id=fi.id)
                db.session.add(sipf)
    deposit.commit()
    return deposit
