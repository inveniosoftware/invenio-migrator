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

from flask import Flask
from flask_cli import FlaskCLI

from invenio_migrator.ext import InvenioMigrator


class Dump(object):
    """Test class."""


class DumpLoader(object):
    """Test class."""


def fetcher(arg1, arg2):
    """Test method."""


def post_task():
    """Test method."""


def test_version():
    """Test version import."""
    from invenio_migrator import __version__
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    FlaskCLI(app)
    ext = InvenioMigrator(app)
    assert 'invenio-migrator' in app.extensions

    app = Flask('testapp')
    FlaskCLI(app)
    ext = InvenioMigrator()
    assert 'invenio-migrator' not in app.extensions
    ext.init_app(app)
    assert 'invenio-migrator' in app.extensions


def test_imp():
    """Test extension initialization."""
    app = Flask('testapp')
    FlaskCLI(app)
    app.config.update(dict(
        MIGRATOR_RECORDS_DUMP_CLS='test_invenio_migrator:Dump',
        MIGRATOR_RECORDS_DUMPLOADER_CLS='test_invenio_migrator:DumpLoader',
        MIGRATOR_RECORDS_PID_FETCHERS=[
            'test_invenio_migrator:fetcher'
        ],
        MIGRATOR_RECORDS_POST_TASK='test_invenio_migrator:post_task'
    ))
    ext = InvenioMigrator(app)
    assert ext.records_dump_cls == Dump
    assert ext.records_dumploader_cls == DumpLoader
    assert ext.records_pid_fetchers == [fetcher]
    assert ext.records_post_task == post_task
