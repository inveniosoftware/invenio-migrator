# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Celery task for records migration."""

from __future__ import absolute_import, print_function

from os.path import isfile, join

from celery import shared_task
from dateutil.parser import parse as iso2dt
from invenio_db import db

from .utils import iso2dt_or_none, logo_ext_wash


@shared_task()
def load_community(data, logos_dir):
    """Load community from data dump.

    :param data: Dictionary containing community data.
    :type data: dict
    :param logos_dir: Path to a local directory with community logos.
    :type logos_dir: str
    """
    from invenio_communities.models import Community
    from invenio_communities.utils import save_and_validate_logo
    logo_ext_washed = logo_ext_wash(data['logo_ext'])
    c = Community(
        id=data['id'],
        id_user=data['id_user'],
        title=data['title'],
        description=data['description'],
        page=data['page'],
        curation_policy=data['curation_policy'],
        last_record_accepted=iso2dt_or_none(data['last_record_accepted']),
        logo_ext=logo_ext_washed,
        ranking=data['ranking'],
        fixed_points=data['fixed_points'],
        created=iso2dt(data['created']),
        updated=iso2dt(data['last_modified']),
    )
    logo_path = join(logos_dir, "{0}.{1}".format(c.id, logo_ext_washed))
    db.session.add(c)
    if isfile(logo_path):
        with open(logo_path, 'rb') as fp:
            save_and_validate_logo(fp, logo_path, c.id)
    db.session.commit()


@shared_task()
def load_featured(data):
    """Load community featuring from data dump.

    :param data: Dictionary containing community featuring data.
    :type data: dict
    """
    from invenio_communities.models import FeaturedCommunity
    obj = FeaturedCommunity(id=data['id'],
                            id_community=data['id_community'],
                            start_date=iso2dt(data['start_date']))
    db.session.add(obj)
    db.session.commit()
