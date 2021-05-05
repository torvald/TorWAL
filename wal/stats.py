import config


def ignore_where():
    where_ignore_string = "1 = 1"
    for pattern in config.IGNORE_PATTERNS:
        where_ignore_string += f" AND active_win not LIKE '{pattern}'"

    return where_ignore_string


def pretty_dur(total_mins):
    hours = int(total_mins / 60)
    mins = str(int(total_mins % 60)).zfill(2)
    return f"{hours}h{mins}m"


def active_windows(connection, limit, since):
    print(f"--- Top {limit} active windows since {since} ---")
    cursor = connection.cursor()

    query = f"""SELECT count(*) as count, active_win, category FROM x_log
            WHERE {config.IS_ACTIVE_WHERE}
            AND timestamp > '{since}'
            AND {ignore_where()}
            GROUP BY active_win
            ORDER by 1 DESC
            LIMIT {limit}"""

    if config.DEBUG:
        print(query)

    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        count = row[0]
        active_win = row[1]
        category = row[2]
        mins = round(count / 6, 2)
        time = pretty_dur(mins)
        print(f"{time} of {active_win} ({category})")


def top_categories(connection, limit, since):
    print(f"--- Top {limit} categories since {since} ---")
    cursor = connection.cursor()

    query = f"""SELECT count(*) as count, category FROM x_log
            WHERE {config.IS_ACTIVE_WHERE}
            AND timestamp > '{since}'
            AND {ignore_where()}
            GROUP BY category
            ORDER by 1 DESC
            LIMIT {limit}"""

    if config.DEBUG:
        print(query)

    cursor.execute(query)
    rows = cursor.fetchall()

    total_ticks = 0
    for row in rows:
        total_ticks += row[0]

    for row in rows:
        count = row[0]
        active_win = row[1] or "Uncatagories"
        mins = round(count / 6, 2)
        time = pretty_dur(mins)
        percent = round(count / total_ticks * 100)
        print(f"{time} ({percent}%) of {active_win}")


def active_time_per_day(connection, limit, since):
    print("--- Active time (at all hours) ---")

    cursor = connection.cursor()
    query = f"""
        select strftime('%Y-%m-%d',timestamp) AS 'day', count(*) from x_log
        WHERE {config.IS_ACTIVE_WHERE}
        AND {ignore_where()}
        AND timestamp > '{since}'
        group by day;
        """

    if config.DEBUG:
        print(query)

    cursor.execute(query)
    rows = cursor.fetchall()
    total = 0
    for row in rows:
        day = row[0]
        active_hours = pretty_dur(row[1] / 6)
        total += row[1]
        print(f"{day}: {active_hours}")
    print(pretty_dur(total / 6), "total")


def show_stats(connection, limit, since):
    active_windows(connection, limit, since)
    top_categories(connection, limit, since)
    active_time_per_day(connection, limit, since)


def update_categories(connection):
    cursor = connection.cursor()
    for pattern, category in config.PATTERNS_CATEGORIES:
        cursor.execute(
            f"update x_log set category = '{category}' where active_win LIKE '{pattern}';"
        )

    connection.commit()
