#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2016 CERN.
# SPDX-License-Identifier: MIT

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
