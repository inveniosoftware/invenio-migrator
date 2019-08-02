# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

r"""Invenio-Communities migration.

Invenio-Communities
-------------------

Dumping data from Legacy
~~~~~~~~~~~~~~~~~~~~~~~~

Dump the models ``User``, ``Community`` and ``FeaturedCommunity``:

.. code-block:: console

   $ inveniomigrator dump users
   $ inveniomigrator dump communities
   $ inveniomigrator dump featured

Prepare a tarbar of community logos:

.. code-block:: console

   $ cd /(invenio instance path)/static/media
   $ tar cvf communities.tar ./communities

This will result in the output files:

- ``users_dump_*.json``
- ``communities_dump_*.json``
- ``featured_dump_*.json``
- ``communities.tar``

Loading data
~~~~~~~~~~~~

Extract the tarball ``communities.tar`` to a ``communities/`` directory:

.. code-block:: console

   $ tar xvf ./communities.tar

Initialize the communities files bucket:

.. code-block:: console

   $ invenio communities init

Load the users, communities and community featurings. Last parameter of
``invenio dumps loadcommunities`` should point to the directory containing
the community logos.

.. code-block:: console

   $ for f in ./users_dump_*.json; do invenio dumps loadusers $f; done
   $ for f in ./communities_dump_*.json; do invenio dumps loadcommunities $f \
           ./communities/; done
   $ for f in ./featured_dump_*.json; do invenio dumps loadfeatured $f; done
"""

from __future__ import absolute_import, print_function

from .utils import dt2iso_or_empty


def get(*args, **kwargs):
    """Get communities."""
    from invenio.modules.communities.models import Community
    q = Community.query
    return q.count(), q.all()


def dump(c, from_date, with_json=True, latest_only=False, **kwargs):
    """Dump the community object as dictionary.

    :param c: Community to be dumped.
    :type c: `invenio.modules.communities.models.Community`
    :returns: Community serialized to dictionary.
    :rtype: dict
    """
    return dict(id=c.id,
                id_user=c.id_user,
                title=c.title,
                description=c.description,
                page=c.page,
                curation_policy=c.curation_policy,
                last_record_accepted=dt2iso_or_empty(c.last_record_accepted),
                logo_ext=c.logo_ext,
                logo_url=c.logo_url,
                ranking=c.ranking,
                fixed_points=c.fixed_points,
                created=c.created.isoformat(),
                last_modified=c.last_modified.isoformat(),
                id_collection_provisional=c.id_collection_provisional,
                id_oairepository=c.id_oairepository,
                id_collection=c.id_collection)
