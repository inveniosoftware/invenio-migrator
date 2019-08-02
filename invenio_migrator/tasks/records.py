# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Celery task for records migration."""

from __future__ import absolute_import, print_function

from celery import shared_task
from invenio_db import db

from ..proxies import current_migrator


@shared_task()
def import_record(data, source_type=None, latest_only=False):
    """Migrate a record from a migration dump.

    :param data: Dictionary for representing a single record and files.
    :param source_type: Determines if the MARCXML or the JSON dump is used.
        Default: ``marcxml``.
    :param latest_only: Determine is only the latest revision should be loaded.
    """
    source_type = source_type or 'marcxml'
    assert source_type in ['marcxml', 'json']

    recorddump = current_migrator.records_dump_cls(
        data,
        source_type=source_type,
        pid_fetchers=current_migrator.records_pid_fetchers,
    )
    try:
        current_migrator.records_dumploader_cls.create(recorddump)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
