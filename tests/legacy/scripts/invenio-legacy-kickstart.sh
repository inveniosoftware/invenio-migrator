#!/usr/bin/env bash
#
# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

export INVENIO_SRCDIR=$(pwd)/invenio
export INVENIO_ADMIN_EMAIL=info@inveniosoftware.org
export INVENIO_WEB_DSTDIR=${VIRTUAL_ENV:=/opt/invenio}
export INVENIO_WEB_HOST=127.0.0.1
export INVENIO_WEB_USER=travis
export INVENIO_WEB_SMTP_PORT=0
export INVENIO_MYSQL_HOST=127.0.0.1
export INVENIO_MYSQL_DBNAME=invenio1
export INVENIO_MYSQL_DBUSER=invenio1
export INVENIO_MYSQL_DBPASS=dbpass123

git clone -b "${LEGACY}" https://github.com/inveniosoftware/invenio.git

./invenio/scripts/provision-mysql.sh
./invenio/scripts/provision-web.sh
#FIXME
mkdir -p "${INVENIO_WEB_DSTDIR}/lib/python/invenio"
ln -s "${INVENIO_WEB_DSTDIR}/lib/python/invenio" "${VIRTUAL_ENV}/lib/python2.7/site-packages/invenio"
./invenio/scripts/create-instance.sh
./invenio/scripts/populate-instance.sh
