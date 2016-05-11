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

"""Proxies for Invenio-Migrator."""

from __future__ import absolute_import, print_function

from os.path import splitext

import arrow
from dojson.contrib.marc21 import marc21
from dojson.contrib.marc21.utils import create_record
from invenio_db import db
from invenio_files_rest.models import Bucket, BucketTag, FileInstance, \
    ObjectVersion
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus, \
    RecordIdentifier
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record
from invenio_records_files.models import RecordsBuckets
from werkzeug.utils import cached_property


class RecordDumpLoader(object):
    """Migrate a record."""

    @classmethod
    def create(cls, dump):
        """Create record based on dump."""
        dump.prepare_revisions()
        dump.prepare_pids()
        dump.prepare_files()

        # Create or update?
        existing_files = []
        if dump.record:
            existing_files = dump.record.get('files', [])
            record = cls.update_record(dump)
            pids = dump.missing_pids
        else:
            record = cls.create_record(dump)
            pids = dump.pids

        if pids:
            cls.create_pids(record.id, pids)

        if dump.files:
            cls.create_files(record, dump.files, existing_files)

        # Update files.
        if dump.is_deleted(record):
            cls.delete_record(record)

        return record

    @classmethod
    def create_record(cls, dump):
        """Create a new record from dump."""
        # Reserve record identifier, create record and recid pid in one
        # operation.
        timestamp, data = dump.pop_first_revision()
        record = Record.create(data)
        record.model.created = timestamp.replace(tzinfo=None)
        RecordIdentifier.insert(dump.recid)
        PersistentIdentifier.create(
            pid_type='recid',
            pid_value=str(dump.recid),
            object_type='rec',
            object_uuid=str(record.id),
            status=PIDStatus.REGISTERED
        )
        db.session.commit()
        return cls.update_record(dump, record=record)

    @staticmethod
    def update_record(dump, record=None):
        """Update an existing record."""
        record = record or dump.record
        for timestamp, revision in dump.revisions:
            record.model.json = revision
            record.model.created = timestamp.replace(tzinfo=None)
            db.session.commit()
        return Record(record.model.json, model=record.model)

    @staticmethod
    def create_pids(record_uuid, pids):
        """Create persistent identifiers."""
        for p in pids:
            PersistentIdentifier.create(
                pid_type=p.pid_type,
                pid_value=p.pid_value,
                pid_provider=p.provider.pid_provider if p.provider else None,
                object_type='rec',
                object_uuid=record_uuid,
                status=PIDStatus.REGISTERED,
            )
        db.session.commit()

    @classmethod
    def delete_record(cls, record):
        """Delete a record and it's persistent identifiers."""
        record.delete()
        PersistentIdentifier.query.filter_by(
            object_type='rec', object_uuid=record.id,
        ).update({PersistentIdentifier.status: PIDStatus.DELETED})
        cls.delete_buckets(record)
        db.session.commit()

    @classmethod
    def create_files(cls, record, files, existing_files):
        """Create files.

        This method is currently limited to a single bucket per record.
        """
        default_bucket = None
        # Look for bucket id in existing files.
        for f in existing_files:
            if 'bucket' in f:
                default_bucket = f['bucket']
                break

        # Create a bucket in default location if none is found.
        if default_bucket is None:
            b = Bucket.create()
            BucketTag.create(b, 'record', str(record.id))
            default_bucket = str(b.id)
            db.session.commit()
        else:
            b = Bucket.get(default_bucket)

        record['files'] = []
        for key, meta in files.items():
            obj = cls.create_file(b, key, meta)
            ext = splitext(obj.key)[1].lower()
            if ext.startswith('.'):
                ext = ext[1:]
            record['files'].append(dict(
                bucket=str(obj.bucket.id),
                key=obj.key,
                version_id=str(obj.version_id),
                size=obj.file.size,
                checksum=obj.file.checksum,
                type=ext,
            ))
        db.session.add(
            RecordsBuckets(record_id=record.id, bucket_id=b.id)
        )
        record.commit()
        db.session.commit()

        return [b]

    @classmethod
    def create_file(self, bucket, key, file_versions):
        """Create a single file with all versions."""
        objs = []
        for file_ver in file_versions:
            f = FileInstance.create().set_uri(
                file_ver['full_path'],
                file_ver['size'],
                'md5:{0}'.format(file_ver['checksum']),
            )
            obj = ObjectVersion.create(bucket, key).set_file(f)
            obj.created = arrow.get(
                file_ver['creation_date']).datetime.replace(tzinfo=None)
            objs.append(obj)

        # Set head version
        db.session.commit()
        return objs[-1]

    @staticmethod
    def delete_buckets(record):
        """Delete the bucket."""
        files = record.get('files', [])
        buckets = set()
        for f in files:
            buckets.add(f.get('bucket'))
        for b_id in buckets:
            b = Bucket.get(b_id)
            b.deleted = True


class RecordDump(object):
    """Record dump wrapper.

    Wrapper around a record dump, with tools for loading the dump. Extend this
    class to provide custom behavior for loading of record dumps.

    Known limitations:

      - Only persistent identifiers present in the last revision of the record
        will be registered.
    """

    def __init__(self, data, source_type='marcxml', latest_only=False,
                 pid_fetchers=None, dojson_model=marc21):
        """Initialize class."""
        self.resolver = Resolver(
            pid_type='recid', object_type='rec', getter=Record.get_record)
        self.data = data
        self.source_type = source_type
        self.latest_only = latest_only
        self.dojson_model = dojson_model
        self.revisions = None
        self.pid_fetchers = pid_fetchers or []

    @cached_property
    def record(self):
        """Get the first revision."""
        try:
            return self.resolver.resolve(self.data['recid'])[1]
        except PIDDoesNotExistError:
            return None

    @cached_property
    def missing_pids(self):
        """Filter persistent identifiers."""
        missing = []
        for p in self.pids:
            try:
                PersistentIdentifier.get(p.pid_type, p.pid_value)
            except PIDDoesNotExistError:
                missing.append(p)
        return missing

    @cached_property
    def recid(self):
        """Get recid."""
        return self.data['recid']

    def _prepare_revision(self, data):
        dt = arrow.get(data['modification_datetime']).datetime

        if self.source_type == 'marcxml':
            val = self.dojson_model.do(create_record(data['marcxml']))
        else:
            val = data['json']

        return (dt, val)

    def prepare_revisions(self):
        """Prepare data."""
        # Prepare revisions
        self.revisions = []

        it = [self.data['record'][0]] if self.latest_only \
            else self.data['record']

        for i in it:
            self.revisions.append(self._prepare_revision(i))

    def prepare_files(self):
        """Get files from data dump."""
        # Prepare files
        files = {}
        for f in self.data['files']:
            k = f['full_name']
            if k not in files:
                files[k] = []
            files[k].append(f)

        # Sort versions
        for k in files.keys():
            files[k].sort(key=lambda x: x['version'])

        self.files = files

    def prepare_pids(self):
        """Prepare persistent identifiers."""
        self.pids = []
        for fetcher in self.pid_fetchers:
            val = fetcher(None, self.revisions[-1][1])
            if val:
                self.pids.append(val)

    def pop_first_revision(self):
        """Get the first revision."""
        return self.revisions.pop(0)

    def is_deleted(self, record=None):
        """Check if record is deleted."""
        record = record or self.revisions[-1][1]
        return any(
            col == 'deleted'
            for col in record.get('collections', [])
        )
