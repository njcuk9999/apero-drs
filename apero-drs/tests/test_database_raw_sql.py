#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Offline regression tests for percent signs in raw database queries."""

from typing import Any

import pytest
import sqlalchemy

from aperocore.core import drs_db


@pytest.mark.parametrize('method', ['get', 'count', 'unique'])
@pytest.mark.parametrize('condition, expected', [
    ('name LIKE "OBJECT%" OR name LIKE "TELLURIC%"',
     ['OBJECT_A', 'TELLURIC_A']),
    ('name = "100%"', ['100%']),
    ('name = "%(name)s"', ['%(name)s']),
    ('id % 2 = 0', ['100%', 'TELLURIC_A']),
    (None, ['%(name)s', '100%', 'CAL', 'OBJECT_A', 'TELLURIC_A']),
])
def test_raw_queries_preserve_percent_signs(
    method: str, condition: str | None, expected: list[str],
) -> None:
    """Check SQLAlchemy dispatch and query results without a remote database.

    :param method: Database reader to exercise.
    :param condition: Raw SQL filter, including literal percent expressions.
    :param expected: Sorted names selected by the filter.
    :return: None.
    """
    pymysql = pytest.importorskip('pymysql')
    mysql_cursor = pymysql.Connection(defer_connect=True).cursor()
    engine = sqlalchemy.create_engine('sqlite://')
    database = drs_db.AperoDatabase.__new__(drs_db.AperoDatabase)
    database.engine = engine
    database.tablename = 'objects'
    statements = []

    def check_dispatch(
        connection: sqlalchemy.Connection, cursor: Any, statement: str,
        parameters: Any, context: Any, executemany: bool,
    ) -> None:
        """Check raw SQL is dispatched without DBAPI interpolation.

        :param connection: Active SQLAlchemy connection.
        :param cursor: SQLite cursor executing the query.
        :param statement: SQL string to execute.
        :param parameters: SQLAlchemy's empty parameter container.
        :param context: Execution context controlling parameter dispatch.
        :param executemany: Whether multiple parameter sets are supplied.
        :return: None.
        """
        assert not parameters
        assert not executemany
        assert context.no_parameters
        assert mysql_cursor.mogrify(statement, None) == statement
        statements.append(statement)

    try:
        with engine.begin() as connection:
            connection.exec_driver_sql(
                'CREATE TABLE objects (id INTEGER, name TEXT)')
            insert_sql = 'INSERT INTO objects VALUES (?, ?)'
            rows = [(1, 'OBJECT_A'), (2, 'TELLURIC_A'), (3, 'CAL'),
                    (4, '100%'), (5, '%(name)s')]
            connection.exec_driver_sql(insert_sql, rows)
        event_args = [engine, 'before_cursor_execute', check_dispatch]
        sqlalchemy.event.listen(*event_args)
        if method == 'get':
            result = database.get('name', condition=condition)
            assert sorted(row[0] for row in result) == expected
        elif method == 'count':
            assert database.count(condition=condition) == len(expected)
        else:
            result = database.unique('name', condition=condition)
            assert sorted(result.tolist()) == expected
        assert len(statements) == 1
    finally:
        engine.dispose()


def test_pymysql_percent_interpolation_reproduces_error() -> None:
    """Reproduce the original driver error offline and verify its bypass."""
    pymysql = pytest.importorskip('pymysql')
    cursor = pymysql.Connection(defer_connect=True).cursor()
    statement = 'SELECT name FROM objects WHERE name LIKE "OBJECT%"'
    with pytest.raises(ValueError, match='unsupported format character'):
        cursor.mogrify(statement, dict())
    assert cursor.mogrify(statement, None) == statement