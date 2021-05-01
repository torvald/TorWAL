# window-activity-logger

Window Activity Logger (WAL!) - a tool to collect and make stats of your windows use (in Linux)

Perfect for tracking home office time!

## Example

```bash
torvald@gauda ~ $ x-log.py --stats --since=2021-04-29 --limit=3
--- Top 3 active windows since 2021-04-29 ---
0h44m of Meet – Introduction to new way of working - Google Chrome (Google Meet)
0h31m of Incident report 2021-04-28 - Quip — Mozilla Firefox (Firefox - Quip)
0h31m of [mosh] WeeChat 3.1 (IRC)
--- Top 3 categories since 2021-04-29 ---
5h36m of Slack
1h49m of Google Meet
1h49m of Firefox (uncategorized)
--- Active time per day (at all hours) ---
2021-04-29: 6h01m
2021-04-30: 8h03m
2021-05-01: 0h52m
14h57m total
```

## How it works

I personally use this for tracking work hours.

Each 10 seconds, or for each _tick_, we save a row in a SQLite3 database what
window (it's title) you are currently active on and for how long you have been
inactive.

A tick counts as active time if you have been idle for less then `IDLE_TIME` (I
use 5 min). If I attend a virtual meeting I use slightly higher thresholds.

I personally check if Slack is open, as queue to whether I'm «working» or not.
If i close Slack, i don't register active time. This is configurable. This has
the effect of making me mindful about closing work related programs when I'm
actually not working but still use my laptop for smaller stuff.

## Usage

### Register a tick

    ./wal.py reg

### Stats

    ./way.py stats [--since YYYY-MM-DD] [--limit 20]

## Support

The standard config and implementation does only support Linux and X window
system, but feel free to add support for others.

## Installation

Crontab only have minutes as its smallest unit, and i wanted to collect data
every 10th second. I could make it into a running daemon, but this was just the
simplest way about:

    crontab -e

and add

    # m h  dom mon dow   command
    * * * * * sleep 0; /path/to/folder/wal.py reg
    * * * * * sleep 10; /path/to/folder/wal.py reg
    * * * * * sleep 20; /path/to/folder/wal.py reg
    * * * * * sleep 30; /path/to/folder/wal.py reg
    * * * * * sleep 40; /path/to/folder/wal.py reg
    * * * * * sleep 50; /path/to/folder/wal.py reg
