# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Errors for migration tasks."""

from __future__ import absolute_import, print_function


class DepositError(Exception):
    """Base class for Deposit migration errors."""

    def __init__(self, pid, *args, **kwargs):
        """Initialize exception.

        :param pid: PersistentIdentifier of the Deposit metadata.
        :type pid: `invenio_pidstore.models.PersistentIdentifier`
        """
        self.pid = pid
        super(DepositError, self).__init__(*args, **kwargs)

    def __str__(self):
        """String representation of the error."""
        return "PID: {pid}".format(pid=self.pid)


class DepositRecidDoesNotExist(DepositError):
    """Deposit record PID does not exist."""

    def __init__(self, pid, recid, *args, **kwargs):
        """Initialize exception."""
        self.recid = recid
        super(DepositRecidDoesNotExist, self).__init__(pid, *args, **kwargs)

    def __str__(self):
        """String representation of the error."""
        return super(DepositRecidDoesNotExist, self).__str__() + \
            ", recid: {recid}".format(recid=self.recid)


class DepositMultipleRecids(DepositError):
    """Deposit metadata is referencing multiple recids."""

    def __init__(self, pid, recids, *args, **kwargs):
        """Initialize exception."""
        self.recids = recids
        super(DepositMultipleRecids, self).__init__(pid, *args, **kwargs)

    def __str__(self):
        """String representation of the error."""
        return super(DepositRecidDoesNotExist, self).__str__() + \
            ", recids: {recids}".format(recids=self.recids)


class UserEmailExistsError(Exception):
    """User email already exists in the database."""


class UserUsernameExistsError(Exception):
    """User username already exists in the database."""
