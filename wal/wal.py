#!/usr/bin/env python3

import argparse
import sqlite3
import sys
from datetime import date

import config
import stats
from utils import cmd_exitcode


def register_activity(connection):
    if config.ACTIVITY_FILTER_CMD:
        if cmd_exitcode(config.ACTIVITY_FILTER_CMD) == 1:
            print("ACTIVITY_FILTER_CMD failed, so we dont register activity now")
            return

    system_interface = config.system_interface()
    idle_sec = system_interface.idle_sec()
    active_window, active_app = system_interface.active_window()

    cursor = connection.cursor()

    insert_query = "INSERT into x_log (idle, active_win, active_app) VALUES (?,?,?)"
    cursor.execute(insert_query, (idle_sec, active_window, active_app))
    connection.commit()


def pre_check():
    for package in config.NEEDED_PACKAGES:
        if cmd_exitcode(f"whereis {package}") != 0:
            print(f"You need to install {package}")


def setup_sqlite():
    connection = sqlite3.connect(config.DATABASE_FILE)
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

    try:
        cursor.execute("ALTER TABLE x_log ADD COLUMN active_app TEXT default null")
    except sqlite3.OperationalError as e:
        assert "duplicate column name: active_app" in str(e)

    return connection


if __name__ == "__main__":
    pre_check()
    connection = setup_sqlite()

    parser = argparse.ArgumentParser(
        prog="wal.py",
        description="Window Activity Logger (WAL!) - a tool to collect and make stats of your window use (in Linux).",
    )

    subparsers = parser.add_subparsers(dest="action")

    reg_parser = subparsers.add_parser("reg", help="Register tick")
    stats_parser = subparsers.add_parser("stats", help="Show stats")
    stats_parser.add_argument(
        "--limit",
        dest="limit",
        help="(stats) Show number of items in stats tables",
        default=10,
        metavar=10,
        type=int,
    )
    stats_parser.add_argument(
        "--since",
        dest="since",
        help="(stats) Show stance since YYYY-MM-DD (defaults to today)",
        default=date.today().strftime("%Y-%m-%d"),
        metavar="YYY-MM-DD",
    )

    args = parser.parse_args()

    if args.action == "stats":
        stats.update_categories(connection)
        stats.show_stats(connection, args.limit, args.since)
    elif args.action == "reg":
        register_activity(connection)
    else:
        parser.print_help(sys.stderr)
