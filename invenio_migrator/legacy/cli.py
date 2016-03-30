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

"""Simple script to dump all records in an Invenio instance to JSON."""

from __future__ import absolute_import, print_function

import json

import click

from .utils import collect_things_entry_points, grouper, init_app_context


@click.group()
def cli():
    """Command for dumping all records as JSON."""
    pass


@cli.command()
@click.argument('thing')
@click.option('-q', '--query', default='')
@click.option('-f', '--from-date', default='1970-01-01 00:00:00')
@click.option('--file-prefix', default=None)
@click.option('--chunk-size', default=1000)
@click.option('-a', '--argument', multiple=True)
def dump(thing, query, from_date, file_prefix, chunk_size, argument):
    """Dump data from Invenio legacy."""
    init_app_context()

    file_prefix = file_prefix if file_prefix else '{0}_dump'.format(thing)
    kwargs = dict(arg.split('=') for arg in argument)

    try:
        thing_func = collect_things_entry_points()[thing]
    except KeyError:
        click.Abort(
            '{0} is not in the list of available things to migrate: '
            '{1}'.format(thing, collect_things_entry_points()))

    click.echo("Querying {0}...".format(thing))
    count, items = thing_func.get(query, from_date, **kwargs)

    progress_i = 0  # Progress bar counter
    click.echo("Dumping {0}...".format(thing))
    with click.progressbar(length=count) as bar:
        for i, chunk_ids in enumerate(grouper(items, chunk_size)):
            with open('{0}_{1}.json'.format(file_prefix, i), 'w') as fp:
                fp.write("[\n")
                for _id in chunk_ids:
                    try:
                        json.dump(
                            thing_func.dump(_id, from_date, **kwargs), fp)
                        fp.write(",")
                    except Exception as e:
                        click.secho("Failed dump {0} {1} ({2})".format(
                            thing, _id, e.message), fg='red')
                    progress_i += 1
                    bar.update(progress_i)

                # Strip trailing comma.
                fp.seek(fp.tell()-1)
                fp.write("\n]")


@cli.command()
@click.argument('thing')
def check(thing):
    """Check data in Invenio legacy."""
    init_app_context()

    try:
        thing_func = collect_things_entry_points()[thing]
    except KeyError:
        click.Abort(
            '{0} is not in the list of available things to migrate: '
            '{1}'.format(thing, collect_things_entry_points()))

    click.echo("Querying {0}...".format(thing))
    count, items = thing_func.get_check()

    i = 0
    click.echo("Checking {0}...".format(thing))
    with click.progressbar(length=count) as bar:
        for _id in items:
            thing_func.check(_id)
            i += 1
            bar.update(i)
