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

"""Module tests."""

from __future__ import absolute_import, print_function

import pytest
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record
from invenio_records.models import RecordMetadata
from invenio_records_files.api import Record as RecordFiles
from invenio_sipstore.models import SIP, RecordSIP, SIPFile

from invenio_migrator.tasks.deposit import load_deposit
from invenio_migrator.tasks.errors import DepositMultipleRecids, \
    DepositRecidDoesNotExist, DepositSIPUserDoesNotExist


def test_deposit_load(dummy_location, deposit_user, deposit_record_pid):
    """Test the deposit loading function."""
    dep1 = dict(sips=[dict(metadata=dict(recid='10'),
                           agents=[dict(user_id=1), ],
                           package='Foobar'), ],
                _p=dict(id='1'))
    dep2 = dict(sips=[dict(metadata=dict(recid='50'),
                           agents=[dict(user_id=1), ],
                           package='Foobar'), ],
                _p=dict(id='2'))
    dep3 = dict(sips=[dict(metadata=dict(recid='10'),
                           agents=[dict(user_id=5), ],
                           package='Foobar'), ],
                _p=dict(id='3'))
    dep4 = dict(sips=[dict(metadata=dict(recid='10'),
                           agents=[dict(user_id=5), ],
                           package='Foobar'),
                      dict(metadata=dict(recid='11'),
                           agents=[dict(user_id=5), ],
                           package='Foobar'), ],
                _p=dict(id='4'))
    load_deposit(dep1)
    pytest.raises(DepositRecidDoesNotExist, load_deposit, dep2)
    pytest.raises(DepositSIPUserDoesNotExist, load_deposit, dep3)
    pytest.raises(DepositMultipleRecids, load_deposit, dep4)


def test_deposit_load_task(dummy_location, deposit_dump, deposit_user,
                           deposit_record_pid):
    """Test the deposit loading task."""

    # Create a user and a record with PID corresponding with test deposit data
    assert RecordMetadata.query.count() == 1
    for dep in deposit_dump:
        load_deposit.delay(dep)
    assert RecordMetadata.query.count() == 2
    res = Resolver(pid_type='depid', object_type='rec',
                   getter=Record.get_record)
    dep_pid, dep_rec = res.resolve('1')
    assert '_deposit' in dep_rec
    assert '_files' in dep_rec
    sip = SIP.query.one()
    assert sip.user_id == deposit_user.id
    rsip = RecordSIP.query.one()
    assert rsip.pid_id == deposit_record_pid.id
    assert rsip.sip_id == sip.id

    # Test RecordsFiles API
    res = Resolver(pid_type='depid', object_type='rec',
                   getter=RecordFiles.get_record)
    dep_pid, dep_recbucket = res.resolve('1')
    files = list(dep_recbucket.files)
    assert files[0]['key'] == 'bazbar.pdf'
    assert files[0]['size'] == 12345
    assert files[0]['checksum'] == "00000000000000000000000000000000"
    assert files[0]['bucket']
    assert SIPFile.query.count() == 1
