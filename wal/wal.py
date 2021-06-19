#!/usr/bin/env python3

import argparse
import sqlite3
import sys
from datetime import date

import config
import stats
import database as db
from graphs import Graphs
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

    reg_parser = subparsers.add_parser("reg", help="Register tick")
    graphs_parser = subparsers.add_parser("graphs", help="Create graphs!")
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
        help="(stats) Show stats since YYYY-MM-DD (defaults to today at 00:00)",
        default=date.today().strftime("%Y-%m-%d"),
        metavar="YYY-MM-DD",
    )

    stats_parser.add_argument(
        "--before",
        dest="before",
        help="(stats) Show stats before YYYY-MM-DD",
        metavar="YYY-MM-DD",
    )

    args = parser.parse_args()

    if args.action == "stats":
        stats.update_categories(connection)
        stats.show_stats(connection, args.limit, args.since, args.before)
    elif args.action == "reg":
        stats.update_categories(connection)
        register_activity(connection)
    elif args.action == "graphs":
        g = Graphs(connection, None, None)
        g.action()
    elif args.action == "migration":
        db.run_migrations(config.DATABASE_FILE)
    else:
        parser.print_help(sys.stderr)
