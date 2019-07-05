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

"""Proxies for Invenio-Migrator."""

from __future__ import absolute_import, print_function

from os.path import splitext

import arrow
from dojson.contrib.marc21 import marc21
from dojson.contrib.marc21.utils import create_record
from flask import current_app as app
from invenio_db import db
from invenio_files_rest.models import Bucket, BucketTag, FileInstance, \
    ObjectVersion
from invenio_files_rest.tasks import remove_file_data
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus, \
    RecordIdentifier
from invenio_pidstore.resolver import Resolver
from invenio_records.models import RecordMetadata
from invenio_records_files.api import Record
from invenio_records_files.models import RecordsBuckets
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.utils import cached_property

from .utils import disable_timestamp


class RecordDumpLoader(object):
    """Migrate a record."""

    @classmethod
    def clean(cls, dump, delete_files=False):
        """Clean a record with all connected objects."""
        app.logger.debug('Clean record {0}'.format(dump.recid))
        record = dump.resolver.resolve(dump.data['recid'])[1]
        # clean deposit
        cls.clean_deposit(record=record, delete_files=delete_files)
        # clean record
        cls.clean_record(dump=dump, record=record, delete_files=delete_files)

    @classmethod
    def _get_deposit(cls, record):
        """Get deposit."""
        app.logger.debug('Get deposit for record {0}'.format(record.id))
        records = RecordMetadata.query.all()
        #  records = RecordMetadata.query.filter([
        #      sqlalchemy.cast(
        #          RecordMetadata.json['recid'],
        #          sqlalchemy.Integer) == sqlalchemy.type_coerce(
        #              int(record['recid']), sqlalchemy.JSON)
        #  ]).all()
        for record_db in records:
            try:
                if record['recid'] == record_db.json['recid']:
                    pid = PersistentIdentifier.query.filter_by(
                        pid_type='depid', object_uuid=str(record_db.id)).one()
                    return Record.get_record(pid.object_uuid)
            except NoResultFound:
                pass
        app.logger.debug('Clean deposit, deposit for the record '
                         '{0} not found'.format(record.id))
        return None

    @classmethod
    def clean_deposit(cls, record, delete_files):
        """Clean deposit."""
        app.logger.debug('Clean deposit for record {0}'.format(record.id))
        deposit = cls._get_deposit(record=record)
        if deposit:
            cls.clean_buckets(record=deposit, delete_files=delete_files)
            cls.clean_pids(deposit)
            db.session.delete(deposit.model)

    @classmethod
    def clean_record(cls, dump, record, delete_files):
        """Clean record."""
        cls.clean_buckets(record, delete_files=delete_files)
        cls.clean_pids(record)
        RecordIdentifier.query.filter_by(recid=dump.recid).delete()
        db.session.delete(record.model)

    @classmethod
    def clean_files(cls, bucket, delete_files):
        """Clean files."""
        for obj in ObjectVersion.query.filter_by(bucket=bucket).all():
            objs_to_file = ObjectVersion.query.filter_by(
                file_id=obj.file_id).count()
            obj.file.writable = True
            db.session.delete(obj)
            if objs_to_file == 1:
                if delete_files:
                    remove_file_data.s(file_id=obj.file_id).apply()
                else:
                    obj.file.delete()

    @classmethod
    def clean_buckets(cls, record, delete_files):
        """Clean buckets."""
        app.logger.debug('Clean bucket for record {0}'.format(record.id))
        for rb in RecordsBuckets.query.filter_by(record_id=record.id).all():
            bucket = rb.bucket
            app.logger.debug('Clean files for bucket {0}'.format(bucket.id))
            cls.clean_files(bucket=bucket, delete_files=delete_files)
            app.logger.debug('Clean tags for bucket {0}'.format(bucket.id))
            for tag in BucketTag.query.filter_by(bucket=bucket).all():
                db.session.delete(tag)
            db.session.delete(rb)
            db.session.delete(bucket)

    @classmethod
    def _get_pids(cls, record):
        """Get all pids."""
        return PersistentIdentifier.query.filter_by(
            object_type='rec', object_uuid=record.id).all()

    @classmethod
    def clean_pids(cls, record):
        """Clean all pids."""
        app.logger.debug('Clean pids and record identifier for '
                         'record {0}'.format(record.id))
        for pid in cls._get_pids(record):
            db.session.delete(pid)

    @classmethod
    def create(cls, dump):
        """Create record based on dump."""
        # If 'record' is not present, just create the PID
        if not dump.data.get('record'):
            try:
                PersistentIdentifier.get(pid_type='recid',
                                         pid_value=dump.recid)
            except PIDDoesNotExistError:
                PersistentIdentifier.create(
                    'recid', dump.recid,
                    status=PIDStatus.RESERVED
                )
                db.session.commit()
            return None

        dump.prepare_revisions()
        dump.prepare_pids()
        dump.prepare_files()

        # Create or update?
        existing_files = []
        if dump.record:
            existing_files = dump.record.get('_files', [])
            record = cls.update_record(revisions=dump.revisions,
                                       created=dump.created,
                                       record=dump.record)
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
    @disable_timestamp
    def create_record(cls, dump):
        """Create a new record from dump."""
        # Reserve record identifier, create record and recid pid in one
        # operation.
        timestamp, data = dump.latest
        record = Record.create(data)
        record.model.created = dump.created.replace(tzinfo=None)
        record.model.updated = timestamp.replace(tzinfo=None)
        RecordIdentifier.insert(dump.recid)
        PersistentIdentifier.create(
            pid_type='recid',
            pid_value=str(dump.recid),
            object_type='rec',
            object_uuid=str(record.id),
            status=PIDStatus.REGISTERED
        )
        db.session.commit()
        return cls.update_record(revisions=dump.rest, record=record,
                                 created=dump.created)

    @classmethod
    @disable_timestamp
    def update_record(cls, revisions, created, record):
        """Update an existing record."""
        for timestamp, revision in revisions:
            record.model.json = revision
            record.model.created = created.replace(tzinfo=None)
            record.model.updated = timestamp.replace(tzinfo=None)
            db.session.commit()
        return Record(record.model.json, model=record.model)

    @classmethod
    def create_pids(cls, record_uuid, pids):
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

        record['_files'] = []
        for key, meta in files.items():
            obj = cls.create_file(b, key, meta)
            ext = splitext(obj.key)[1].lower()
            if ext.startswith('.'):
                ext = ext[1:]
            record['_files'].append(dict(
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

    @classmethod
    def delete_buckets(cls, record):
        """Delete the bucket."""
        files = record.get('_files', [])
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

        val['_collections'] = self.data.get('collections', [])

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

    @property
    def created(self):
        """Get creation date."""
        return self.revisions[0][0]

    @property
    def latest(self):
        """Get the first revision."""
        return self.revisions[0]

    @property
    def rest(self):
        """The list of old revisions."""
        return self.revisions[1:]

    def is_deleted(self, record=None):
        """Check if record is deleted."""
        record = record or self.revisions[-1][1]
        return any(
            col == 'deleted'
            for col in record.get('collections', [])
        )
