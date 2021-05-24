import config


def ignore_where():
    where_ignore_string = "1 = 1"
    for pattern in config.IGNORE_PATTERNS:
        where_ignore_string += f" AND active_win not LIKE '{pattern}'"

    return where_ignore_string


def pretty_dur(total_mins):
    sign = "-" if total_mins < 0 else ""
    total_mins = abs(total_mins)
    hours = int(total_mins / 60)
    mins = str(int(total_mins % 60)).zfill(2)
    return f"{sign}{hours}h{mins}m"


def active_windows(connection, limit, timestamp_where):
    print(f"--- Top {limit} active windows ---")
    cursor = connection.cursor()

    query = f"""SELECT count(*) as count, active_win, category FROM x_log
            WHERE {config.IS_ACTIVE_WHERE}
            AND {timestamp_where}
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


def top_uncategorised(connection, limit, timestamp_where):
    print(f"--- Top {limit} uncategories ---")
    cursor = connection.cursor()

    query = f"""SELECT count(*) as ticks, active_win FROM x_log
            WHERE {config.IS_ACTIVE_WHERE}
            AND {timestamp_where}
            AND {ignore_where()}
            AND category is null
            GROUP BY active_win
            ORDER BY ticks DESC
            LIMIT {limit}"""

    if config.DEBUG:
        print(query)

    cursor.execute(query)
    rows = cursor.fetchall()

    for row in rows:
        ticks = row[0]
        active_win = row[1]
        mins = round(ticks / 6, 2)
        time = pretty_dur(mins)
        print(f"{time} of {active_win}")


def top_categories(connection, limit, timestamp_where):
    print(f"--- Top {limit} categories ---")
    cursor = connection.cursor()

    query = f"""SELECT count(*) as count, category FROM x_log
            WHERE {config.IS_ACTIVE_WHERE}
            AND {timestamp_where}
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


def active_time_per_day(connection, limit, timestamp_where):
    print("--- Active time (at all hours) ---")

    cursor = connection.cursor()
    query = f"""
        select strftime('%Y-%m-%d',timestamp) AS 'date',
               strftime('%w',timestamp) AS 'day',
               count(*)
        FROM x_log
        WHERE {config.IS_ACTIVE_WHERE}
        AND {ignore_where()}
        AND {timestamp_where}
        group by date;
        """

    if config.DEBUG:
        print(query)

    cursor.execute(query)
    rows = cursor.fetchall()

    total = 0
    time_bank = 0

    for row in rows:
        intraday_balance = 0
        date, day, ticks = row[0], int(row[1]), row[2]
        total += ticks

        if day in [1, 2, 3, 4, 5] and date not in config.LEAVE_DAYS:
            intraday_balance = ticks - (7.5 * 60 * 6)
        else:  # Sat or Sun or LEAVE_DAYS
            intraday_balance = ticks

        time_bank += intraday_balance
        pretty_intraday_balance = pretty_dur(intraday_balance / 6)
        pretty_active_hours = pretty_dur(ticks / 6)
        name_of_days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        print(
            f"{date} ({name_of_days[day]}): {pretty_active_hours} ({pretty_intraday_balance})"
        )

    print(pretty_dur(total / 6), "total")
    print(pretty_dur(time_bank / 6), "off balance during this period")


def show_stats(connection, limit, since, before):
    timestamp_where = f"timestamp > '{since}'"
    if before:
        timestamp_where += f" AND timestamp < '{before}'"

    top_uncategorised(connection, limit, timestamp_where)
    active_windows(connection, limit, timestamp_where)
    top_categories(connection, limit, timestamp_where)
    active_time_per_day(connection, limit, timestamp_where)


def update_categories(connection):
    cursor = connection.cursor()
    for pattern, category in config.PATTERNS_CATEGORIES:
        cursor.execute(
            f"update x_log set category = '{category}' where active_win LIKE '{pattern}';"
        )

    connection.commit()
