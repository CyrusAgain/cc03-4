"""Database access. MySQL (XAMPP) is the default; SQLite is available for tests/offline use.

Both backends are used through the same tiny interface (execute / commit / rollback / close)
with `?` placeholders, so the rest of the app does not care which one is behind it.
The tables (schema.py) and, for MySQL, the database itself are created automatically.
"""
import re
import sqlite3
from decimal import Decimal

import click
from flask import current_app, g

from schema import MYSQL_SCHEMA, SQLITE_SCHEMA

_schema_checked = set()


class DatabaseUnavailable(Exception):
    """MySQL cannot be reached (usually: MySQL is not started in XAMPP)."""


class MySQLCursorAdapter:
    """Makes a PyMySQL cursor look like a sqlite3 one (Decimal -> float)."""

    def __init__(self, cursor):
        self.cursor = cursor

    @staticmethod
    def _normalize(row):
        if row is None:
            return None
        return {key: (float(value) if isinstance(value, Decimal) else value) for key, value in row.items()}

    def fetchone(self):
        return self._normalize(self.cursor.fetchone())

    def fetchall(self):
        return [self._normalize(row) for row in self.cursor.fetchall()]

    @property
    def lastrowid(self):
        return self.cursor.lastrowid

    @property
    def rowcount(self):
        return self.cursor.rowcount


class MySQLConnectionAdapter:
    """Lets the app write sqlite-style SQL (`?` placeholders) against MySQL."""

    def __init__(self, connection):
        self.connection = connection

    @staticmethod
    def _translate_sql(sql):
        sql = re.sub(r"\s+COLLATE\s+NOCASE\b", "", sql, flags=re.IGNORECASE)
        return sql.replace("?", "%s")

    def execute(self, sql, params=()):
        cursor = self.connection.cursor()
        cursor.execute(self._translate_sql(sql), tuple(params or ()))
        return MySQLCursorAdapter(cursor)

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()


def _database_backend():
    return str(current_app.config.get("DB_BACKEND", "mysql")).lower()


def _connect_mysql():
    try:
        import pymysql
        from pymysql.cursors import DictCursor
    except ImportError as exc:
        raise DatabaseUnavailable(
            "PyMySQL is not installed. Run setup_xampp.bat once (or: pip install PyMySQL bcrypt)."
        ) from exc

    cfg = current_app.config
    name = cfg.get("MYSQL_DATABASE", "recipe_pantry")
    params = dict(
        host=cfg.get("MYSQL_HOST", "127.0.0.1"),
        port=int(cfg.get("MYSQL_PORT", 3306)),
        user=cfg.get("MYSQL_USER", "root"),
        password=cfg.get("MYSQL_PASSWORD", ""),
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
        connect_timeout=5,
    )
    try:
        try:
            connection = pymysql.connect(database=name, **params)
        except pymysql.err.OperationalError as exc:
            if not exc.args or exc.args[0] != 1049:      # 1049 = unknown database -> create it
                raise
            bootstrap = pymysql.connect(**params)
            with bootstrap.cursor() as cur:
                cur.execute(
                    "CREATE DATABASE IF NOT EXISTS `%s` CHARACTER SET utf8mb4 "
                    "COLLATE utf8mb4_unicode_ci" % name.replace("`", "")
                )
            bootstrap.commit()
            bootstrap.close()
            connection = pymysql.connect(database=name, **params)
    except (pymysql.MySQLError, OSError) as exc:
        raise DatabaseUnavailable(
            "Could not connect to MySQL at %s:%s as '%s' (%s)." % (params["host"], params["port"], params["user"], exc)
        ) from exc
    return MySQLConnectionAdapter(connection)


def _run_mysql_schema(conn):
    sql = re.sub(r"(?m)^\s*--.*$", "", MYSQL_SCHEMA)
    for statement in sql.split(";"):
        statement = statement.strip()
        if statement:
            conn.execute(statement)
    conn.commit()


def _upgrade_schema_once(conn, backend, database_key):
    """Create any missing tables, once per process per database."""
    key = (backend, database_key)
    if key in _schema_checked:
        return
    if backend == "sqlite":
        conn.executescript(SQLITE_SCHEMA)
        conn.commit()
    else:
        _run_mysql_schema(conn)
    _schema_checked.add(key)


def get_db():
    if "db" not in g:
        backend = _database_backend()
        if backend == "sqlite":
            database_path = current_app.config["DATABASE"]
            connection = sqlite3.connect(database_path, detect_types=sqlite3.PARSE_DECLTYPES)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            g.db = connection
            database_key = database_path
        elif backend == "mysql":
            g.db = _connect_mysql()
            database_key = (
                current_app.config.get("MYSQL_HOST", "127.0.0.1"),
                current_app.config.get("MYSQL_PORT", 3306),
                current_app.config.get("MYSQL_DATABASE", "recipe_pantry"),
            )
        else:
            raise RuntimeError("Unsupported DB_BACKEND: %s" % backend)
        _upgrade_schema_once(g.db, backend, database_key)
    return g.db


def close_db(e=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    """Create the tables (also happens automatically on first use)."""
    conn = get_db()
    if _database_backend() == "sqlite":
        conn.executescript(SQLITE_SCHEMA)
        conn.commit()
    else:
        _run_mysql_schema(conn)


@click.command("init-db")
def init_db_command():
    """Flask CLI command: `flask --app app init-db`."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
