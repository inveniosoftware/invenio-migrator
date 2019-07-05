# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
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

"""Circulation Locations dump functions."""

from .utils import datetime_toutc


def get_loan_requests(barcode):
    """Dump all the loan requests for a given item.

    :returns: list of dictionaries.
    """
    try:
        from invenio.dbquery import run_sql
    except ImportError:
        from invenio.legacy.dbquery import run_sql

    return [dict(id=lr[0],
                 user_id=_get_user_id_from_borrower(lr[1]),
                 period_of_interes_from=datetime_toutc(lr[2]).isoformat(),
                 period_of_interest_from=datetime_toutc(lr[3]).isoformat(),
                 status=lr[4],
                 notes=lr[5],
                 request_date=datetime_toutc(lr[6]).isoformat())
            for lr in run_sql(
                    'SELECT id, id_crcBORROWER, period_of_interest_from, '
                    'period_of_interest_to, status, notes, request_date '
                    'FROM crcLOANREQUEST WHERE barcode = %s',
                    (barcode, ), run_on_slave=True)]


def get_loans(barcode):
    """Dump all the loans for a given item.

    :return: list of dictionaries.
    """
    try:
        from invenio.dbquery import run_sql
    except ImportError:
        from invenio.legacy.dbquery import run_sql

    return [dict(id=l[0],
                 user_id=_get_user_id_from_borrower(l[1]),
                 loaned_on=datetime_toutc(l[2]).isoformat(),
                 returned_on=datetime_toutc(l[3]).isoformat() if l[3] else '',
                 due_date=datetime_toutc(l[4]).isoformat(),
                 number_of_renewals=l[5],
                 overdue_letter_number=l[6],
                 overdue_letter_date=l[7],
                 status=l[8],
                 type=l[9],
                 notes=l[10])
            for l in run_sql(
                    'SELECT id, id_crcBORROWER, loaned_on, returned_on, '
                    'due_date, number_of_renewals, overdue_letter_number, '
                    'overdue_letter_date, status, type, notes '
                    'FROM crcLOAN WHERE barcode = %s',
                    (barcode, ), run_on_slave=True)]


def _get_user_id_from_borrower(borrower_id):
    """Try to find the user equivalent for the borrower.

    The matching is done via email as this is the only common field available.
    If there is not any match or there is more than one the borrower
    information is returned as ``borrower_id::CCID::email``.

    :param borrower_id:
    :return: User id if found, otherwise borrower information.
    """
    try:
        from invenio.dbquery import run_sql
    except ImportError:
        from invenio.legacy.dbquery import run_sql

    borrower = run_sql('SELECT id, ccid, email FROM crcBORROWER WHERE id = %s',
                       (borrower_id, ), run_on_slave=True)
    if not borrower or len(borrower) != 1:
        return None
    borrower = borrower[0]

    user = run_sql('SELECT id FROM user WHERE email = %s',
                   (borrower[2], ), run_on_slave=True)
    if not user or len(user) != 1:
        return '{0}::{1}::{2}'.format(*borrower)
    else:
        return user[0][0]


def get(query=None, from_date='1970-01-01 00:00:00', **kwargs):
    """Get items.

    :param query: Not used
    :param from_date: only get items older than this date.
    :returns: list of dictionaries containing all the item's information.
    """
    try:
        from invenio.dbquery import run_sql
    except ImportError:
        from invenio.legacy.dbquery import run_sql

    res = [dict(barcode=i[0],
                 recid=i[1],
                 location_id=[2][0],
                 collection=i[3],
                 location=i[4],
                 description=i[5],
                 loan_period=i[6],
                 status=i[7],
                 creation_date=datetime_toutc(i[8]).isoformat(),
                 modification_date=datetime_toutc(i[9]).isoformat(),
                 number_of_requests=i[10],
                 expected_arrival_date=i[11])
            for i in run_sql(
                    'SELECT barcode, id_bibrec, id_crcLIBRARY, collection, '
                    'location, description, loan_period, status, '
                    'creation_date, modification_date, number_of_requests, '
                    'expected_arrival_date FROM crcITEM '
                    'WHERE creation_date >= %s',
                    (from_date, ), run_on_slave=True) ]
    return len(res), res


def dump(item, *args, **kwargs):
    """Dump item information together with the loans and loan requests.

    .. note::

        There is a known problem with respect to migrating
        ``crcBORROWER``, there is no link whatsoever to the user table, so
        there could be some borrowers without user representation. For these
        cases we store ``borrower_id::CCID::email`` for future reference, i.e.
        ``1234::56789::john.doe@cern.ch``.

    :param item: Item information as return by the ``get`` function.
    :return: Dictionary with the dump.
    """
    item_dump = dict(
        item,
        requests=get_loan_requests(item['barcode']),
        loans=get_loans(item['barcode']),
    )

    return item_dump
