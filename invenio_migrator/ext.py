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

"""Utilities for migrating past Invenio versions to Invenio 3.0."""

from __future__ import absolute_import, print_function

from werkzeug.utils import cached_property, import_string

from .cli import dumps
from .records import RecordDump


def config_imp_or_default(app, config_var_imp, default):
    """Import config var import path or use default value."""
    imp = app.config.get(config_var_imp)
    return import_string(imp) if imp else default


class _InvenioMigratorState(object):
    """State object for migrator."""

    def __init__(self, app):
        """State initialization."""
        self.app = app

    @cached_property
    def records_cls(self):
        return config_imp_or_default(
            self.app, 'MIGRATOR_RECORDS_CLASS', RecordDump)

    @cached_property
    def records_post_task(self):
        return config_imp_or_default(
            self.app, 'MIGRATOR_RECORDS_POST_TASK', None)

    @cached_property
    def records_pids_fetcher(self):
        return config_imp_or_default(
            self.app, 'MIGRATOR_RECORDS_PIDS_FETCHER', None)

    @cached_property
    def files_post_task(self):
        return config_imp_or_default(
            self.app, 'MIGRATOR_FILES_POST_TASK', None)


class InvenioMigrator(object):
    """Invenio-Migrator extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app.config)
        app.extensions['invenio-migrator'] = _InvenioMigratorState(app)
        app.cli.add_command(dumps)

    def init_config(self, config):
        """Initialize config."""
        config.setdefault('MIGRATOR_FILES_POST_TASK', None)
        config.setdefault('MIGRATOR_RECORDS_POST_TASK', None)
        config.setdefault('MIGRATOR_RECORDS_PID_FETCHERS', None)
        config.setdefault('MIGRATOR_RECORDS_PID_KEY', 'control_number')
