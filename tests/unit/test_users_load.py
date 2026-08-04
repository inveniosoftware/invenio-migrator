# SPDX-FileCopyrightText: 2016 CERN.
# SPDX-License-Identifier: MIT

"""Module tests."""

from __future__ import absolute_import, print_function

from invenio_accounts.models import User

from invenio_migrator.tasks.users import load_user


def test_users_load(db, users_dump):
    """Load the users JSON dump."""
    for data in users_dump:
        load_user.delay(data)
    db.session.commit()
    assert User.query.count() == 3
    u1, u2, u3 = User.query.all()
    assert u1.email == 'user1@invenio.org'
    assert u2.email == 'user2@invenio.org'
    assert u3.password is None
