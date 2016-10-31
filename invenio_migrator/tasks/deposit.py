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
import arrow

from celery import shared_task
from celery.utils.log import get_task_logger
from os.path import splitext


from .utils import empty_str_if_none
from .errors import DepositMultipleRecids

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
    from invenio_pidstore.models import PersistentIdentifier, PIDStatus, \
        RecordIdentifier

    deposit = Record.create(data=data)

    created = arrow.get(data['_p']['created']).datetime
    deposit.model.created = created.replace(tzinfo=None)
    depid = deposit['_p']['id']
    pid = PersistentIdentifier.create(
        pid_type='depid',
        pid_value=str(depid),
        object_type='rec',
        object_uuid=str(deposit.id),
        status=PIDStatus.REGISTERED
    )
    if RecordIdentifier.query.get(int(depid)) is None:
        RecordIdentifier.insert(int(depid))
    deposit.commit()
    return deposit, pid


def create_files_and_sip(deposit, dep_pid):
    """Create deposit Bucket, Files and SIPs."""
    from invenio_pidstore.errors import PIDDoesNotExistError
    from invenio_pidstore.models import PersistentIdentifier, PIDStatus, \
        RecordIdentifier
    from invenio_sipstore.errors import SIPUserDoesNotExist
    from invenio_sipstore.models import SIP, RecordSIP, SIPFile
    from invenio_files_rest.models import Bucket, FileInstance, ObjectVersion
    from invenio_records_files.models import RecordsBuckets
    from invenio_db import db
    buc = Bucket.create()
    recbuc = RecordsBuckets(record_id=deposit.id, bucket_id=buc.id)
    db.session.add(recbuc)
    deposit.setdefault('_deposit', dict())
    deposit.setdefault('_buckets', dict(deposit=str(buc.id)))
    deposit.setdefault('_files', list())
    files = deposit.get('files', [])
    sips = deposit.get('sips', [])

    # Look for prereserved DOI (and recid)
    if 'drafts' in deposit:
        drafts = list(deposit['drafts'].items())
        if len(drafts) != 1:
            logger.exception('Deposit {dep_pid} has multiple drafts'.format(
                dep_pid=dep_pid))
        if len(drafts) == 1:
            draft_type, draft = drafts[0]
            draft_v = draft['values']
            if 'prereserve_doi' in draft_v:
                pre_recid = str(draft_v['prereserve_doi']['recid'])
                pre_doi = str(draft_v['prereserve_doi']['doi'])

                # If pre-reserve info available, try to reserve 'recid'
                try:
                    pid = PersistentIdentifier.get(pid_type='recid',
                                                   pid_value=str(pre_recid))
                except PIDDoesNotExistError:
                    # Reserve recid
                    pid = PersistentIdentifier.create(
                        pid_type='recid',
                        pid_value=str(pre_recid),
                        object_type='rec',
                        status=PIDStatus.RESERVED
                    )

                # If pre-reserve info available, try to reserve 'doi'
                try:
                    pid = PersistentIdentifier.get(pid_type='doi',
                                                   pid_value=str(pre_doi))
                except PIDDoesNotExistError:
                    # Reserve DOI
                    pid = PersistentIdentifier.create(
                        pid_type='doi',
                        pid_value=str(pre_doi),
                        object_type='rec',
                        status=PIDStatus.RESERVED
                    )

                if RecordIdentifier.query.get(int(pre_recid)) is None:
                    RecordIdentifier.insert(int(pre_recid))


    # Store the path -> FileInstance mappings for SIPFile creation later
    dep_file_instances = list()

    for file_ in files:
        size = file_['size']
        key=file_['name']
        # Warning: Assumes all checksums are MD5!
        checksum = 'md5:{0}'.format(file_['checksum'])
        fi = FileInstance.create()
        fi.set_uri(file_['path'], size, checksum)
        ov = ObjectVersion.create(buc, key, _file_id=fi.id)
        ext = splitext(ov.key)[1].lower()
        if ext.startswith('.'):
            ext = ext[1:]
        file_meta = dict(
            bucket=str(ov.bucket.id),
            key=ov.key,
            checksum=ov.file.checksum,
            size=ov.file.size,
            version_id=str(ov.version_id),
            type=ext,
        )
        deposit['_files'].append(file_meta)
        dep_file_instances.append((file_['path'], fi))


    # Get a recid from SIP information
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

    for idx, sip in enumerate(sips):
        agent = None
        user_id = None
        if sip['agents']:
            agent = dict(
                ip_address=empty_str_if_none(
                    sip['agents'][0].get('ip_address', "")),
                email=empty_str_if_none(
                    sip['agents'][0].get('email_address', "")),
            )
            user_id = sip['agents'][0]['user_id']
        if user_id == 0:
            user_id = None
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
            sip = SIP.create(sip_format,
                             content,
                             agent=agent)

        # Attach recid to SIP
        if recid:
            try:
                pid = PersistentIdentifier.get(pid_type='recid',
                                               pid_value=str(recid))
                record_sip = RecordSIP(sip_id=sip.id, pid_id=pid.id)
                db.session.add(record_sip)
            except PIDDoesNotExistError:
                logger.exception('Record {recid} referred in '
                                 'Deposit {depid} does not exists.'.format(
                                     recid=recid, depid=dep_pid.pid_value))
                if deposit['_p']['submitted'] == True:
                    logger.exception('Pair {recid}/{depid} was submitted,'
                                     ' (should it be unpublished?).'.format(
                                         recid=recid, depid=dep_pid.pid_value))
                else:
                    logger.exception('Pair {recid}/{depid} was not submitted.'.
                        format(recid=recid, depid=dep_pid.pid_value))

                # Reserve recid
                pid = PersistentIdentifier.create(
                    pid_type='recid',
                    pid_value=str(recid),
                    object_type='rec',
                    status=PIDStatus.RESERVED
                )

                if RecordIdentifier.query.get(int(recid)) is None:
                    RecordIdentifier.insert(int(recid))
        if idx == 0:
            for fp, fi in dep_file_instances:
                sipf = SIPFile(sip_id=sip.id, filepath=fp, file_id=fi.id)
                db.session.add(sipf)
    deposit.commit()
    return deposit
