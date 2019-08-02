# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from __future__ import absolute_import, print_function

import hashlib
from os.path import join

from invenio_accounts.testutils import create_test_user
from invenio_communities.models import Community, FeaturedCommunity
from invenio_communities.utils import initialize_communities_bucket
from invenio_files_rest.models import Location, ObjectVersion

from invenio_migrator.tasks.communities import load_community, load_featured


def test_communities_load(db, communities_dump, featured_dump, logos_dir):
    """Load the communities JSON dump."""
    # Create a single user (with id=1) to meet the community's FK constraint.
    create_test_user('test@invenio.org', password='123456')

    # Initialize communities bucket (requires a default Location)
    loc = Location(name='local', uri='file:///tmp', default=True)
    db.session.add(loc)
    db.session.commit()
    initialize_communities_bucket()

    # Load the communities
    for data in communities_dump:
        load_community.delay(data, logos_dir)

    # Check if community was loaded correctly
    assert Community.query.count() == 1
    c = Community.query.first()
    assert c.title == 'Invenio Community'
    assert c.id == 'invenio'

    # Check object metadata
    assert ObjectVersion.query.count() == 1  # Check if the logo was created
    assert ObjectVersion.query.first().key == 'invenio/logo.jpg'

    # Open the original logo from test data and check if checksums match
    with open(join(logos_dir, 'invenio.jpg'), 'rb') as fp:
        logo_checksum = hashlib.md5(fp.read()).hexdigest()
        assert ObjectVersion.query.first().file.checksum == \
            'md5:{0}'.format(logo_checksum)

    # Load the community featurings
    for data in featured_dump:
        load_featured.delay(data)

    # Make sure they are loaded correctly
    assert FeaturedCommunity.query.count() == 1
    fc = FeaturedCommunity.query.first()
    assert fc.community.id == c.id
