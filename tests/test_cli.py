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

"""Module tests."""

from __future__ import absolute_import, print_function

from os.path import join

from click.testing import CliRunner

from invenio_migrator.cli import inspectrecords, loadrecords


def test_inspectrecords(script_info, datadir):
    """Test inspect records CLI."""
    runner = CliRunner()
    filepath = join(datadir, 'records.json')

    result = runner.invoke(inspectrecords, [filepath], obj=script_info)
    assert result.exit_code == 0

    result = runner.invoke(
        inspectrecords, ['--recid', '11782', filepath], obj=script_info)
    assert result.exit_code == 0

    result = runner.invoke(
        inspectrecords, ['--recid', '11782', '--files', filepath],
        obj=script_info)
    assert result.exit_code == 0

    result = runner.invoke(
        inspectrecords, ['--recid', '11782', '--json', filepath],
        obj=script_info)
    assert result.exit_code == 0

    result = runner.invoke(
        inspectrecords, ['--recid', '11782', '--marcxml', filepath],
        obj=script_info)
    assert result.exit_code == 0

    result = runner.invoke(
        inspectrecords, ['--recid', '12345', '--files', filepath],
        obj=script_info)
    print(result.output)
    assert result.exit_code == 0


def test_loadrecords(db, dummy_location, script_info, datadir):
    """Test load records CLI."""
    runner = CliRunner()
    filepath = join(datadir, 'records.json')

    result = runner.invoke(loadrecords, [filepath], obj=script_info)
    assert result.exit_code == 0
