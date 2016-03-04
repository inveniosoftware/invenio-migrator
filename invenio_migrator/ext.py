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

from flask import current_app
from werkzeug.utils import import_string


class InvenioMigrator(object):
    """Invenio-Migrator extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)
            self.files_post_task = None

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app.config)
        app.extensions['invenio-migrator'] = self

    def init_config(self, config):
        """Initialize config."""
        config.setdefault('MIGRATOR_FILES_POST_TASK', None)

    def files_post_task_factory(self, bucket_id, key):
        """Factory for sending Celery task after files creation."""
        if self.files_post_task is None:
            task_imp = current_app.config['MIGRATOR_FILES_POST_TASK']
            if task_imp:
                self.files_post_task = import_string(task_imp)
            else:
                self.files_post_task = False

        if self.files_post_task:
            self.files_post_task.delay(bucket_id, key)
