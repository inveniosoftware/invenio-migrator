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

"""Pytest configuration."""

from __future__ import absolute_import, print_function

import json
import os
import shutil
import tempfile
import uuid
from os.path import dirname, join

import pytest
from flask import Flask
from flask_babelex import Babel
from flask_celeryext import FlaskCeleryExt
from flask.cli import ScriptInfo
from flask_oauthlib.client import OAuth as FlaskOAuth
from invenio_accounts import InvenioAccounts
from invenio_accounts.models import User
from invenio_communities import InvenioCommunities
from invenio_db import db as db_
from invenio_db import InvenioDB
from invenio_deposit import InvenioDeposit
from invenio_files_rest import InvenioFilesREST
from invenio_files_rest.models import Bucket, Location, ObjectVersion
from invenio_jsonschemas.ext import InvenioJSONSchemas
from invenio_oauthclient import InvenioOAuthClient
from invenio_pidstore import InvenioPIDStore
from invenio_pidstore.fetchers import FetchedPID
from invenio_pidstore.models import PersistentIdentifier, PIDStatus, \
    RecordIdentifier
from invenio_pidstore.resolver import Resolver
from invenio_records import InvenioRecords
from invenio_records.api import Record
from invenio_sipstore.ext import InvenioSIPStore
from six import BytesIO
from sqlalchemy_utils.functions import create_database, database_exists

from invenio_migrator.ext import InvenioMigrator
from invenio_migrator.records import RecordDump

"""Pytest configuration."""


@pytest.yield_fixture(scope='session', autouse=True)
def app(request):
    """Flask application fixture."""
    app_ = Flask('testapp')
    app_.config.update(
        CELERY_ALWAYS_EAGER=True,
        CELERY_RESULT_BACKEND="cache",
        CELERY_CACHE_BACKEND="memory",
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        TESTING=True,
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI',
            'sqlite:///:memory:'),
        SECURITY_PASSWORD_SALT='TEST',
        SECRET_KEY='TEST',
    )
    FlaskCeleryExt(app_)
    InvenioDB(app_)
    InvenioRecords(app_)
    InvenioDeposit(app_)
    InvenioJSONSchemas(app_)
    InvenioAccounts(app_)
    InvenioCommunities(app_)
    InvenioPIDStore(app_)
    InvenioSIPStore(app_)
    Babel(app_)
    InvenioFilesREST(app_)
    InvenioMigrator(app_)
    FlaskOAuth(app_)
    InvenioOAuthClient(app_)

    with app_.app_context():
        yield app_


@pytest.fixture
def script_info(app):
    """Get ScriptInfo object for testing CLI."""
    return ScriptInfo(create_app=lambda info: app)


@pytest.yield_fixture()
def db(app):
    """Setup database."""
    if not database_exists(str(db_.engine.url)):
        create_database(str(db_.engine.url))
    db_.create_all()
    yield db_
    db_.session.remove()
    db_.drop_all()


@pytest.yield_fixture()
def dummy_location(db):
    """File system location."""
    tmppath = tempfile.mkdtemp()

    loc = Location(
        name='testloc',
        uri=tmppath,
        default=True
    )
    db.session.add(loc)
    db.session.commit()

    yield loc

    shutil.rmtree(tmppath)


@pytest.fixture()
def datadir():
    """Get data directory."""
    return join(dirname(__file__), '..', 'data')


@pytest.fixture()
def logos_dir(datadir):
    """Get data directory."""
    return join(datadir, 'community_logos')


@pytest.fixture()
def records_json(datadir):
    """Load records json."""
    with open(join(datadir, 'records.json')) as fp:
        records = json.load(fp)
    return records


@pytest.fixture()
def communities_dump(datadir):
    """Load test data of dumped communities.

    :returns: Loaded dump of communities as a list of dict.
    :rtype: list
    """
    with open(join(datadir, 'communities.json')) as fp:
        records = json.load(fp)
    return records


@pytest.fixture()
def deposit_user(db):
    """Test user for deposit loading."""
    u1 = User(id=1, email='user@invenio.org',
              password='change_me', active=True)

    db.session.add(u1)
    db.session.commit()
    return u1


@pytest.fixture()
def deposit_record_pid(db):
    """Test record PID for deposit loading."""
    rec = Record.create({'title': 'Test'})
    rec_pid = PersistentIdentifier.create(
        pid_type='recid',
        pid_value='10',
        object_type='rec',
        object_uuid=rec.id,
        status=PIDStatus.REGISTERED,
    )
    db.session.commit()
    return rec_pid


@pytest.fixture()
def deposit_dump(datadir):
    """Load test data of dumped deposits.

    :returns: Loaded dump of deposits as a list of dict.
    :rtype: list
    """
    with open(join(datadir, 'deposit.json')) as fp:
        records = json.load(fp)
    return records


@pytest.fixture()
def featured_dump(datadir):
    """Load test data of dumped community featurings.

    :returns: Loaded dump of community featurings as a list of dict.
    :rtype: list
    """
    with open(join(datadir, 'featured.json')) as fp:
        records = json.load(fp)
    return records


@pytest.fixture()
def users_dump(datadir):
    """Load test data of dumped users.

    :returns: Loaded dump of users as a list of dict.
    :rtype: list
    """
    with open(join(datadir, 'users.json')) as fp:
        records = json.load(fp)
    return records


@pytest.fixture()
def record_db(db):
    """Load records JSON."""
    id_ = uuid.uuid4()
    record = Record.create({
        'title': 'Test record',
        'recid': 11782
    }, id_=id_)
    PersistentIdentifier.create(
        pid_type='recid',
        pid_value='11782',
        status=PIDStatus.REGISTERED,
        object_type='rec',
        object_uuid=id_,
    )
    RecordIdentifier.insert(11782)
    db.session.commit()
    return record


@pytest.fixture()
def record_pid(db, record_db):
    """Create record pid."""
    pid = PersistentIdentifier.create(
        pid_type='doi',
        pid_value='10.5281/zenodo.11782',
        status=PIDStatus.REGISTERED,
        object_type='rec',
        object_uuid=record_db.id,
    )
    db.session.commit()
    return pid


@pytest.fixture()
def oauthclient_dump(datadir):
    """Load oauthclient JSON."""
    with open(join(datadir, 'oauthclient.json')) as fp:
        oauth = json.load(fp)
    return oauth['remoteaccounts'], oauth['remotetokens']


@pytest.fixture()
def oauth2server_dump(datadir):
    """Load oauth2server JSON."""
    with open(join(datadir, 'oauth2server.json')) as fp:
        oauth = json.load(fp)
    return oauth['clients'], oauth['tokens']


@pytest.fixture()
def record_file(db, dummy_location):
    """Create record pid."""
    data = b'testfile'
    b = Bucket.create()
    obj = ObjectVersion.create(
        b, 'CERN_openlab_Parin_Porecha.pdf', stream=BytesIO(data))
    db.session.commit()
    return dict(
        bucket=str(obj.bucket_id),
        key=obj.key,
        size=obj.file.size,
        checksum=obj.file.checksum,
    )


@pytest.fixture()
def record_dump(records_json):
    """A record dump."""
    def doi_fetcher(record_uuid, data):
        if 'doi' in data:
            return FetchedPID(
                pid_type='doi', pid_value=data['doi'], provider=None
            )
        return None
    return RecordDump(
        records_json[0], source_type='json', pid_fetchers=[doi_fetcher])


@pytest.fixture()
def resolver():
    """PID resolver."""
    return Resolver(
        pid_type='recid', object_type='rec', getter=Record.get_record)
