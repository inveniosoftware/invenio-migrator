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

"""Test legacy record dump."""

import datetime
from click.testing import CliRunner

from invenio_migrator.legacy.cli import dump as dump_cli
from invenio_migrator.legacy.circulation_locations import (
    dump as dump_location,
    get as get_location
)
from invenio_migrator.legacy.circulation_items import (
    dump as dump_item,
    get as get_item,
    get_loan_requests,
    get_loans
)


def test_get_location():
    """Test get location."""
    count, locations = get_location()

    assert count == 2
    assert locations[0] == {'id': 1,
                            'name': 'Atlantis Main Library',
                            'address': 'CH-1211 Geneva 23',
                            'email': 'atlantis@cds.cern.ch',
                            'phone': '1234567',
                            'type': 'main',
                            'notes': ''}
    assert locations[1] == {'id': 2,
                            'name': 'Atlantis HEP Library',
                            'address': 'CH-1211 Geneva 21',
                            'email': 'atlantis.hep@cds.cern.ch',
                            'phone': '1234567',
                            'type': 'external',
                            'notes': ''}

    # dump doesn't change the location, just returns
    assert locations[0] == dump_location(locations[0])
    assert locations[1] == dump_location(locations[1])

    assert get_location(only_used=True) == (count, locations)


def test_location_cli():
    """Test CLI."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            dump_cli, ['circ_locations', ])
        assert result.exit_code == 0


def test_get_item():
    """Test get item."""
    count, items = get_item()

    assert count == 18
    assert items[0] == dict(barcode='bc-34001',
                            recid=34,
                            location_id=2,
                            collection='',
                            location='ABC-123',
                            description='Book',
                            loan_period='4 weeks',
                            status='available',
                            creation_date='2008-07-20T22:00:00+00:00',
                            modification_date='2008-07-20T22:00:00+00:00',
                            number_of_requests=0,
                            expected_arrival_date='')


def test_get_loans():
    """Test get loans."""
    loans = get_loans('bc-31001')

    assert len(loans) == 1

    loan = loans[0]

    assert loan['status'] == 'on loan'
    assert loan['user_id'] == 5


def test_get_loan_requests():
    """Test get loan requests."""
    requests = get_loan_requests('bc-29001')

    assert len(requests) == 1

    request = requests[0]
    assert request['status'] == 'pending'
    assert request['user_id'] == 6


def test_dump_item():
    """Test dump item."""
    item = dump_item(get_item()[1][2])

    assert item['barcode'] == 'bc-33001'
    assert len(item['loans']) == 1
    assert len(item['requests']) == 1


def test_item_cli():
    """Test CLI."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            dump_cli, ['circ_items', ])
        assert result.exit_code == 0
