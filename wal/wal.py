#!/usr/bin/env python3

import argparse
import sqlite3
import sys
from datetime import date

try:
    import config
except ImportError:
    print("You need to make a copy of the config file first.")
    print("$ cp config.py.example config.py")
    print("$ vim config.py")
    raise SystemExit

import stats
import database as db
from utils import cmd_exitcode


def register_activity(connection):
    if config.ACTIVITY_FILTER_CMD:
        if cmd_exitcode(config.ACTIVITY_FILTER_CMD) == 1:
            print("ACTIVITY_FILTER_CMD failed, so we dont register activity now")
            return

    system_interface = config.system_interface()
    idle_sec = system_interface.idle_sec()
    active_window, active_app = system_interface.active_window()
    ssid = system_interface.current_ssid()

    cursor = connection.cursor()

    insert_query = "INSERT into x_log (idle, active_win, active_app, ssid) VALUES (?,?,?,?)"
    cursor.execute(insert_query, (idle_sec, active_window, active_app, ssid))
    connection.commit()


def pre_check():
    for package in config.NEEDED_PACKAGES:
        if cmd_exitcode(f"whereis {package}") != 0:
            print(f"You need to install {package}")


if __name__ == "__main__":
    pre_check()
    connection = db.setup_sqlite(config.DATABASE_FILE)

    parser = argparse.ArgumentParser(
        prog="wal.py",
        description="Window Activity Logger (WAL!) - a tool to collect and make stats of your window use (in Linux).",
    )

    subparsers = parser.add_subparsers(dest="action")

    back_fill_parser = subparsers.add_parser("back_fill", help="Register tick")
    reg_parser = subparsers.add_parser("reg", help="Register tick")
    stats_parser = subparsers.add_parser("stats", help="Show stats")
    migration_parser = subparsers.add_parser("migration", help="Run DB migrations")

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
        help="(stats) Show stats since YYYY-MM-DD (defaults to first of the month at 00:00)",
        default=date.today().replace(day=1).strftime("%Y-%m-%d"),
        metavar="YYY-MM-DD",
    )
    stats_parser.add_argument(
        "--before",
        dest="before",
        help="(stats) Show stats before YYYY-MM-DD",
        metavar="YYY-MM-DD",
    )

    back_fill_parser.add_argument(
        "--start",
        dest="start",
        help="(stats) Show stats since YYYY-MM-DD (defaults to first of the month at 00:00)",
        metavar="YYY-MM-DD",
    )
    back_fill_parser.add_argument(
        "--end",
        dest="end",
        help="(stats) Show stats before YYYY-MM-DD",
        metavar="YYY-MM-DD",
    )

    args = parser.parse_args()

    if args.action == "stats":
        stats.update_categories(connection)
        stats.show_stats(connection, args.limit, args.since, args.before)
    elif args.action == "reg":
        register_activity(connection)
    elif args.action == "back_fill":
        db.back_fill(connection, args.start, args.end)
    elif args.action == "migration":
        db.run_migrations(config.DATABASE_FILE)
    else:
        parser.print_help(sys.stderr)
