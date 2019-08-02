# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utilities for migrating past Invenio versions to Invenio 3.0.

Invenio-Migrator consists of two parts:

- **Dumpers:** Tools for dumping data from an existing Invenio 1.2 or 2.x
  installation into a JSON file.
- **Loaders:** Tools for loading an Invenio legacy dump into an Invenio 3
  installation.

Dumping data
------------
First install Invenio-Migrator on your legacy installation (see
:ref:`install`). You now the ``invenio-migrator`` CLI availble to dump your
data:

.. code-block:: console

   $ inveniomigrator --help
   Usage: inveniomigrator [OPTIONS] COMMAND [ARGS]...

     Command for dumping legacy installation into a file JSON.

   Options:
     --help  Show this message and exit.

   Commands:
     dump  Dump data from Invenio legacy.


Records/files
~~~~~~~~~~~~~
You can use the CLI to dump e.g. records and files:

.. code-block:: console

   $ inveniomigrator dump records --query collection:preprints

This will dump the records and files in chunks of 1000 records into JSON files
in the current working directory. For each record Invenio-Migrator will dump:

- Record revisions in MARCXML and JSON
- Files for a record.

Loading data
------------
First install Invenio-Migrator on your Invenio 3 installation (see
:ref:`install`). This adds a ``dumps`` command to your instance CLI, which you
can use to load the record dumps:

.. code-block:: console

   $ <instance cmd> dumps loadrecords /path/to/records_dump_0.json

By default the MARCXML for each record is used to for loading the record. If
you wish to use the JSON for each record instead, simply use the
``--source-type json`` option to above command.


Customizing loading
-------------------
In case you need custom loading behavior of your dumps, you can subclass the
two classes :py:data:`invenio_migrator.records.RecordDump` and
:py:data:`invenio_migrator.records.RecordDumpLoader`. See API documentation for
further details.
"""

from __future__ import absolute_import, print_function

from .version import __version__

__all__ = ('__version__', 'InvenioMigrator')
