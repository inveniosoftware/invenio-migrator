#!/usr/bin/env sh
# SPDX-FileCopyrightText: 2016 CERN.
# SPDX-License-Identifier: MIT

pydocstyle invenio_migrator tests && \
isort -rc -c -df **/*.py && \
check-manifest --ignore ".travis-*" && \
sphinx-build -qnNW docs docs/_build/html && \
py.test tests/unit/ && \
sphinx-build -qnNW -b doctest docs docs/_build/doctest
