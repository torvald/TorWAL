import datetime as dt
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


def back_fill(connection, start, end):
    cursor = connection.cursor()

    t_start = dt.datetime.strptime(start, "%Y-%m-%d %H:%M")
    t_end = dt.datetime.strptime(end, "%Y-%m-%d %H:%M")
    interval = dt.timedelta(minutes=30)

    period_start = t_start - (t_start - dt.datetime.min) % interval
    while period_start < t_end:
        period_end = period_start + interval
        timestamp_where = f"timestamp >= '{period_start}' AND timestamp < '{period_end}'"
        query = f"select count(*) FROM x_log WHERE {timestamp_where}"
        cursor.execute(query)
        row = cursor.fetchone()

        if 180-row[0] > 0:
            print(f"Backfilling {180-row[0]} in period {period_start} and {period_end}")
            for _ in range(180-row[0]):
                insert_query = "INSERT into x_log (timestamp, idle, category, active_app) VALUES (?,?,?,?)"
                cursor.execute(insert_query, (period_start, 0, "backfill", "torwal"))
        period_start = period_end
    connection.commit()
