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

"""CDS record specific functions."""

def json_converter(marcxml):
    """TODO: Docstring for json_converter.

    :param marcxml: TODO
    :returns: TODO

    """
    from dojson.contrib.marc21.utils import create_record
    from cds_dojson.marc21 import marc21

    blob = create_record(marcxml)
    try:
        data = marc21.do(blob)
        for missing in marc21.missing(blob):
            # TODO: Log missing tags!
            data[missing] = blob[missing]
        return data
    except Exception:
        # TODO: Log error when creating the json
        return blob
