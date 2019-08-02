# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
