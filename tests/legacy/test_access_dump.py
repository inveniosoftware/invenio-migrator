# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016, 2017 CERN.
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

from click.testing import CliRunner

from invenio_migrator.legacy.cli import dump as dump_cli
from invenio_migrator.legacy.access import (dump as dump_access, get as
                                            get_access)


def test_dump_action():
    """Test single action dump."""
    action = get_access('viewrestrcoll')
    action_dump = dump_access(action[1][0])

    assert action_dump
    assert action_dump['name'] == 'viewrestrcoll'
    assert len(action_dump['roles']) == 5

    roles = action_dump['roles']
    assert roles[0] == {
        'users': {'jekyll@cds.cern.ch'},
        'parameters': {'collection': {'Theses', 'Drafts'}, },
        'name': 'thesesviewer',
        'firerole_def': 'allow group "Theses and Drafts viewers"',
        'id': 16L,
        'description': 'Theses and Drafts viewer'
    }


def test_get_action():
    """Test get action."""
    action = get_access('viewrestrcoll')
    assert action[0] == 1
    assert action[1] == [
        {'allowedkeywords': 'view restricted collection',
         'optional': 'collection',
         'id': 38L,
         'name': 'viewrestrcoll'}
    ]

    actions = get_access('%')
    assert actions[0] == 63
    assert actions[0] == len(actions[1])

    actions = get_access('viewrestr%')
    assert actions[0] == 3
    assert [a['name'] for a in actions[1]
            ] == ['viewrestrcoll', 'viewrestrcomment', 'viewrestrdoc']


def test_cli():
    """Test CLI."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(dump_cli, ['access', '-q', '%'])
        assert result.exit_code == 0
