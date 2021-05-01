#!/usr/bin/env python3

import sqlite3
import sys
from datetime import date

import config
from utils import cmd_exitcode

def register_activity(connection):
    if config.ACTIVITY_FILTER_CMD:
        if cmd_exitcode(config.ACTIVITY_FILTER_CMD) == 1:
            print("ACTIVITY_FILTER_CMD failed, so we dont register activity now")
            return

    system_interface = config.system_interface()
    idle_sec = system_interface.idle_sec()
    active_window = system_interface.active_window()

    cursor = connection.cursor()

    insert_query = (
        f"INSERT into x_log (idle, active_win) VALUES ('{idle_sec}', '{active_window}')"
    )
    insert_query.replace("'", "")

    cursor.execute(insert_query)
    connection.commit()


def pre_check():
    # Pre-check
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
    return connection


def pretty_dur(total_mins):
    hours = int(total_mins / 60)
    mins = str(int(total_mins % 60)).zfill(2)
    return f"{hours}h{mins}m"


def show_stats(connection, other_args):
    today = date.today()
    since = today.strftime("%Y-%m-%d")

    limit = 10
    for arg in other_args:
        if "--since" in arg:
            since = arg.split("=")[1]
        if "--limit" in arg:
            limit = arg.split("=")[1]

    print(f"--- Top {limit} active windows since {since} ---")
    cursor = connection.cursor()
    cursor.execute(
        f"""SELECT count(*) as count, active_win, category FROM x_log
            WHERE {config.IS_ACTIVE_WHERE}
            AND timestamp > '{since}'
            AND {config.IGNORE_WHERE}
            GROUP BY active_win
            ORDER by 1 DESC
            LIMIT {limit}"""
    )
    rows = cursor.fetchall()
    for row in rows:
        count = row[0]
        active_win = row[1]
        category = row[2]
        mins = round(count / 6, 2)
        time = pretty_dur(mins)
        print(f"{time} of {active_win} ({category})")

    print(f"--- Top {limit} categories since {since} ---")
    cursor.execute(
        f"""SELECT count(*) as count, category FROM x_log
            WHERE {config.IS_ACTIVE_WHERE}
            AND timestamp > '{since}'
            AND {config.IGNORE_WHERE}
            GROUP BY category
            ORDER by 1 DESC
            LIMIT {limit}"""
    )
    rows = cursor.fetchall()
    for row in rows:
        count = row[0]
        active_win = row[1] or "Uncatagories"
        mins = round(count / 6, 2)
        time = pretty_dur(mins)
        print(f"{time} of {active_win}")

    print("--- Active time (at all hours) ---")
    cursor.execute(
        f"""
        select strftime('%Y-%m-%d',timestamp) AS 'day', count(*) from x_log
        WHERE {config.IS_ACTIVE_WHERE} AND {config.IGNORE_WHERE}
        AND timestamp > '{since}'
        group by day;
        """
    )
    rows = cursor.fetchall()
    total = 0
    for row in rows:
        day = row[0]
        active_hours = pretty_dur(row[1] / 6)
        total += row[1]
        print(f"{day}: {active_hours}")
    print(pretty_dur(total / 6), "total")


def update_categories(connection):
    cursor = connection.cursor()
    for pattern, category in config.PATTERNS_CATEGORIES:
        cursor.execute(
            f"update x_log set category = '{category}' where active_win LIKE '{pattern}';"
        )

    connection.commit()


if __name__ == "__main__":
    pre_check()
    connection = setup_sqlite()

    if "--stats" in sys.argv:
        update_categories(connection)
        other_args = sys.argv[2:]
        show_stats(connection, other_args)
    else:
        register_activity(connection)

# battery0_percent = cmd_output("acpi | grep 'battery 0' | egrep '[0-9]*%' -o").strip()
# battery1_percent = cmd_output("acpi | grep 'Battery 1' | egrep '[0-9]*%' -o").strip()
