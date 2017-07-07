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

"""Utilities for migrating past Invenio versions to Invenio 3.0."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.2.2',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
]

extras_require = {
    'docs': [
        'Sphinx>=1.4.2,<1.6',
    ],
    'loader': [
        'Flask-CeleryExt>=0.2.0',
        'Flask>=0.11.1',
        'arrow>=0.7.0',
        'dojson>=1.0.0',
        'invenio-db[versioning]>=1.0.0b3',
        'invenio-files-rest>=1.0.0a13',
        'invenio-pidstore>=1.0.0b1',
        'invenio-records>=1.0.0b1',
        'invenio-records-files>=1.0.0a7',
        'invenio-sipstore>=1.0.0a3',
        # FIXME
        'elasticsearch<3.0.0,>=2.0.0',
        'elasticsearch-dsl<3.0.0,>=2.0.0',
        'celery<4.0,>=3.1',
    ],
    'deposit': [
        'invenio-deposit>=1.0.0a6',
    ],
    'communities': [
        'invenio-communities>=1.0.0a13',
    ],
    'userprofiles': [
        'invenio-userprofiles>=1.0.0a8',
    ],
    'oauthclient': [
        'invenio-oauthclient>=1.0.0a7',
    ],
    'oauth2server': [
        'invenio-oauth2server>=1.0.0a12',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = [
    'pytest-runner>=2.7.0',
]

install_requires = [
    'Click>=6.3',
    'six>=1.10.0',
    'Werkzeug>=0.11.4',
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_migrator', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-migrator',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio migration',
    license='GPLv2',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/invenio-migrator',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'inveniomigrator = invenio_migrator.legacy.cli:cli',
        ],
        'invenio_base.apps': [
            'invenio_migrator = invenio_migrator.ext:InvenioMigrator',
        ],
        'invenio_celery.tasks': [
            'communities = invenio_migrator.tasks.communities',
            'deposit = invenio_migrator.tasks.deposit',
            'oauthclient = invenio_migrator.tasks.oauthclient',
            'oauth2server = invenio_migrator.tasks.oauth2server',
            'records = invenio_migrator.tasks.records',
            'users = invenio_migrator.tasks.users',
        ],
        'invenio_migrator.things': [
            'clients = invenio_migrator.legacy.clients',
            'communities = invenio_migrator.legacy.communities',
            'deposit = invenio_migrator.legacy.deposit',
            'featured = invenio_migrator.legacy.featured_communities',
            'files = invenio_migrator.legacy.bibdocfile',
            'records = invenio_migrator.legacy.records',
            'remoteaccounts = invenio_migrator.legacy.remoteaccounts',
            'remotetokens = invenio_migrator.legacy.remotetokens',
            'tokens = invenio_migrator.legacy.tokens',
            'userexts = invenio_migrator.legacy.userexts',
            'users = invenio_migrator.legacy.users',
        ]
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Development Status :: 3 - Alpha',
    ],
)
