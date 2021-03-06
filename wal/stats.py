import config
import time
import datetime
from utils import histogram_bar


def active_where():
    is_active_where = "("
    is_active_where += f"idle < {config.IDLE_TIME_GENERAL} or (active_win LIKE '{config.VIDEO_CONFERENCING_APP_PATTERN}' and idle < {config.IDLE_TIME_VIDEO_CONFERENCING})"
    for ssid in config.SSIDS_PATTERNS:
        is_active_where += f" or ssid LIKE '{ssid}'"
    is_active_where += ")"
    return is_active_where

def ignore_where():
    where_ignore_string = "1 = 1"
    for pattern in config.IGNORE_PATTERNS:
        where_ignore_string += f" AND active_win not LIKE '{pattern}'"

    return where_ignore_string


def pretty_dur(total_mins):
    sign = "-" if total_mins < 0 else " "
    total_mins = abs(total_mins)
    hours = str(int(total_mins / 60)).zfill(2)
    mins = str(int(total_mins % 60)).zfill(2)
    return f"{sign}{hours}h{mins}m"


def active_windows(connection, limit, timestamp_where):
    print(f"--- Top {limit} active windows ---")
    cursor = connection.cursor()

    query = f"""SELECT count(*) as count, active_win, category FROM x_log
            WHERE {active_where()}
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
            WHERE {active_where()}
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
            WHERE {active_where()}
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
        WHERE {active_where()}
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

    last_date = None

    for row in rows:
        intraday_balance = 0
        date, day, ticks = row[0], int(row[1]), row[2]
        total += ticks

        # Generating timeseries in sqlite is non-trivial, so instead of joining
        # that into the query, i use this hack to fill in the dates with no
        # data
        if last_date:
            this_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            next_date = last_date + datetime.timedelta(days=1)
            while next_date != this_date:
                null_date = next_date.strftime("%Y-%m-%d")
                null_day = next_date.strftime("%a")
                null_ticks = pretty_dur(0)
                print(f"{null_date} ({null_day}): {null_ticks}")
                next_date = next_date + datetime.timedelta(days=1)
        last_date = datetime.datetime.strptime(date, "%Y-%m-%d")

        if day in [1, 2, 3, 4, 5] and date not in config.LEAVE_DAYS:
            intraday_balance = ticks - (7.5 * 60 * 6)
        else:  # Sat or Sun or LEAVE_DAYS
            intraday_balance = ticks

        time_bank += intraday_balance
        pretty_intraday_balance = pretty_dur(intraday_balance / 6)
        pretty_active_hours = pretty_dur(ticks / 6)
        name_of_days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        histogram = create_histogram(connection, date)
        print(
            f"{date} ({name_of_days[day]}): {pretty_active_hours} ({pretty_intraday_balance}) {histogram}"
        )

    print(pretty_dur(total / 6), "total")
    print(pretty_dur(time_bank / 6), "off balance during this period")


def create_histogram(connection, date):

    group_size_in_minutes = 30
    time_interval_windows = 60 * group_size_in_minutes
    # i.e. for 30 minutes gropus, there will be 48 groups
    groups_total = int((24 * 60 * 60) / time_interval_windows)

    timestamp_start_of_day = int(
        time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple())
        / time_interval_windows
    )

    cursor = connection.cursor()
    query = f"""
        select strftime('%Y-%m-%d',timestamp) AS 'date',
               strftime('%s',timestamp) / (60*{group_size_in_minutes}) as time_interval,
               count(*)
        FROM x_log
        WHERE {active_where()}
        AND date = '{date}'
        GROUP BY time_interval
        """

    if config.DEBUG:
        print(query)

    cursor.execute(query)
    rows = cursor.fetchall()

    groups = {}
    for row in rows:
        # To make the numbers relative to the intra day
        timestamp = row[1] - timestamp_start_of_day
        count = row[2]
        groups[timestamp] = count

    histogram = ""
    # We only record each 10 sec, so max value can be max 180 for i.e 30 min (1800s)
    max_value = time_interval_windows / 10
    for i in range(groups_total):
        histogram += histogram_bar(groups[i], max_value) if i in groups else " "

    return f"|{histogram}|"


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
