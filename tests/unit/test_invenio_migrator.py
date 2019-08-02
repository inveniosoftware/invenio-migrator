# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from __future__ import absolute_import, print_function

from flask import Flask

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
    ext = InvenioMigrator(app)
    assert 'invenio-migrator' in app.extensions

    app = Flask('testapp')
    ext = InvenioMigrator()
    assert 'invenio-migrator' not in app.extensions
    ext.init_app(app)
    assert 'invenio-migrator' in app.extensions


def test_imp():
    """Test extension initialization."""
    app = Flask('testapp')
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
