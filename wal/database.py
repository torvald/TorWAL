import sqlite3


def setup_sqlite(database_file):
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    cursor.execute(
        """CREATE TABLE if not exists x_log(
        id INTEGER PRIMARY KEY,
        active_win TEXT,
        category TEXT,
        idle INTEGER,
        timestamp DATETIME DEFAULT (datetime('now','localtime'))
    );"""
    )
    return connection


def run_migrations(database_file):
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()

    try:
        cursor.execute("ALTER TABLE x_log ADD COLUMN active_app TEXT default null")
    except sqlite3.OperationalError as e:
        assert "duplicate column name: active_app" in str(e)

    try:
        cursor.execute("ALTER TABLE x_log ADD COLUMN ssid TEXT default null")
    except sqlite3.OperationalError as e:
        assert "duplicate column name: ssid" in str(e)
