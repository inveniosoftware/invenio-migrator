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

"""CLI interface for Invenio 3 to load legacy dump."""

from __future__ import absolute_import, print_function

import json
import sys

import click
from celery import chain
from flask_cli import with_appcontext

from .proxies import current_migrator
from .tasks.records import import_record


@click.group()
def dumps():
    """Migration commands."""


@dumps.command()
@click.argument('sources', type=click.File('r'), nargs=-1)
@click.option('--source-type', '-t',  type=click.Choice(['json', 'marcxml']),
              default='marcxml', help='Whether to use JSON or MARCXML.')
@with_appcontext
def loadrecords(sources, source_type):
    """Load records migration dump."""
    for idx, source in enumerate(sources, 1):
        click.echo('Loading dump {0} of {1} ({2})'.format(idx, len(sources),
                                                          source.name))
        data = json.load(source)
        with click.progressbar(data) as records:
            for item in records:
                if current_migrator.records_post_task:
                    chain(
                        import_record.s(item, source_type=source_type),
                        current_migrator.records_post_task.s()
                    )()
                else:
                    import_record.delay(item, source_type=source_type)


@dumps.command()
@click.argument('sources', type=click.File('r'), nargs=-1)
@click.option('--recid', type=int)
@click.option('--files', 'entity', flag_value='files')
@click.option('--json', 'entity', flag_value='json')
@click.option('--marcxml', 'entity', flag_value='marcxml')
@with_appcontext
def inspectrecords(sources, recid, entity=None):
    """Inspect records in a migration dump."""
    for idx, source in enumerate(sources, 1):
        click.echo('Loading dump {0} of {1} ({2})'.format(idx, len(sources),
                                                          source.name))
        data = json.load(source)

        # Just print record identifiers if none are selected.
        if not recid:
            click.secho('Record identifiers', fg='green')
            total = 0
            for r in (d['recid'] for d in data):
                click.echo(r)
                total += 1
            click.echo('{0} records found in dump.'.format(total))
            return

        data = list(filter(lambda d: d['recid'] == recid, data))

        if not data:
            click.secho("Record not found.", fg='yellow')
            return

        for record in data:
            if entity is None:
                click.echo(json.dumps(record, indent=2))
            if entity == 'files':
                click.secho('Files', fg='green')
                click.echo(
                    json.dumps(record['files'], indent=2))

            if entity == 'json':
                click.secho('Records (JSON)', fg='green')
                for revision in record['record']:
                    click.secho('Revision {0}'.format(
                        revision['modification_datetime']), fg='yellow')
                    click.echo(json.dumps(revision['json'], indent=2))

            if entity == 'marcxml':
                click.secho('Records (MARCXML)', fg='green')
                for revision in record['record']:
                    click.secho(
                        'Revision {0}'.format(revision['marcxml']),
                        fg='yellow')
                    click.echo(revision)


def loadcommon(sources, load_task, *args, **kwargs):
    """Common helper function for load simple objects.

    Note: Extra `args` and `kwargs` are passed to the `load_task` function.

    :param sources: JSON source files with dumps
    :type sources: list of str (filepaths)
    :param load_task: Shared task which loads the dump.
    :type load_task: function
    """
    click.echo('Loading dumps started.')
    for idx, source in enumerate(sources, 1):
        click.echo('Loading dump {0} of {1} ({2})'.format(idx, len(sources),
                                                          source.name))
        data = json.load(source)
        with click.progressbar(data) as data_bar:
            for d in data_bar:
                load_task.delay(d, *args, **kwargs)


@dumps.command()
@click.argument('sources', type=click.File('r'), nargs=-1)
@click.argument('logos_dir', type=click.Path(exists=True), default=None)
@with_appcontext
def loadcommunities(sources, logos_dir):
    """Load communities."""
    from invenio_migrator.tasks.communities import load_community
    loadcommon(sources, load_community, logos_dir)


@dumps.command()
@click.argument('sources', type=click.File('r'), default=sys.stdin)
@with_appcontext
def loadfeatured(sources):
    """Load community featurings."""
    from invenio_migrator.tasks.communities import load_featured
    loadcommon(sources, load_featured)


@dumps.command()
@click.argument('sources', type=click.File('r'), nargs=-1)
@with_appcontext
def loadusers(sources):
    """Load users."""
    from .tasks.users import load_user
    loadcommon(sources, load_user)


@dumps.command()
@click.argument('sources', type=click.File('r'), nargs=-1)
@with_appcontext
def loaddeposit(sources):
    """Load deposit."""
    from .tasks.deposit import load_deposit
    loadcommon(sources, load_deposit)


@dumps.command()
@click.argument('sources', type=click.File('r'), nargs=-1)
@with_appcontext
def loadremoteaccounts(sources):
    """Load remote accounts."""
    from .tasks.oauthclient import load_remoteaccount
    loadcommon(sources, load_remoteaccount)


@dumps.command()
@click.argument('sources', type=click.File('r'), nargs=-1)
@with_appcontext
def loadremotetokens(sources):
    """Load remote tokens."""
    from .tasks.oauthclient import load_remotetoken
    loadcommon(sources, load_remotetoken)


@dumps.command()
@click.argument('sources', type=click.File('r'), nargs=-1)
@with_appcontext
def loaduserexts(sources):
    """Load user identities (legacy UserEXT)."""
    from .tasks.oauthclient import load_userext
    loadcommon(sources, load_userext)


@dumps.command()
@click.argument('sources', type=click.File('r'), nargs=-1)
@with_appcontext
def loadtokens(sources):
    """Load server tokens."""
    from .tasks.oauth2server import load_token
    loadcommon(sources, load_token)


@dumps.command()
@click.argument('sources', type=click.File('r'), nargs=-1)
@with_appcontext
def loadclients(sources):
    """Load server clients."""
    from .tasks.oauth2server import load_client
    loadcommon(sources, load_client)
