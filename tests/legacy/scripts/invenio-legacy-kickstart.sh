#!/usr/bin/env bash
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
