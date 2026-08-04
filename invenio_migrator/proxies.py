# SPDX-FileCopyrightText: 2016 CERN.
# SPDX-License-Identifier: MIT

"""Proxies for Invenio-Migrator."""

from __future__ import absolute_import, print_function

from flask import current_app
from werkzeug.local import LocalProxy

current_migrator = LocalProxy(
    lambda: current_app.extensions['invenio-migrator'])
"""Proxy to current migration context."""
