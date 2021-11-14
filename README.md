# TorWAL

Previously known as `window-activity-logger`, but as a friend pointed out, `TorWAL` was more fitting.

Yeah, so this is my Window Activity Logger (WAL, not an overload term at all!) - a tool to collect and make stats of your windows use (in Linux).

## Example

```bash
$ torwal stats --since 2021-09-01 --before 2021-10-01
--- Top 10 uncategories ---
[...]
--- Top 10 active windows ---
[...]
--- Top 10 categories ---
 49h42m (31%) of Slack
 27h55m (18%) of Firefox (uncategorized)
 18h47m (12%) of Video Meeting
 15h19m (10%) of Firefox - Business internal documentaion tool
 10h36m (7%) of Terminal (uncategorized)
 10h13m (6%) of VIM (in dev folders)
 09h52m (6%) of Terminal (in dev folders)
 07h42m (5%) of Firefox - Monitoring stack tools
 04h54m (3%) of Firefox - Google Cloud Platform
 03h55m (2%) of Firefox - GitHub Pull Request
--- Active time (at all hours) ---
2021-09-01 (Wed):  08h04m ( 00h34m) |                    ▃▃▇▇▇▇▇▇▇▇▇▅▆▇▇▅▄▁▇▇▅       |
2021-09-02 (Thu):  06h40m (-00h49m) |                    ▆▇▇▇▇▆▇▇▇▇▇▇▅▇▇▂            |
2021-09-03 (Fri):  05h43m (-01h46m) |                     ▇▇▇▆▇▅▂▇▇▇▇▇▄▃ ▅           |
2021-09-04 (Sat):  00h00m
2021-09-05 (Sun):  00h23m ( 00h23m) |                                        ▄▂      |
2021-09-06 (Mon):  06h17m (-01h12m) |                     ▅▂▇▇▇▇▇▇▇▇▇▇▇▇▇▇▁          |
2021-09-07 (Tue):  07h03m (-00h26m) |                      ▄▇▇▅▇▇▇▇▇▇▇▇▇▇▇▃▆         |
2021-09-08 (Wed):  06h40m (-00h49m) |                     ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▄          ▁ |
2021-09-09 (Thu):  06h43m (-00h47m) |                    ▁▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇  ▂         |
2021-09-10 (Fri):  06h24m (-01h05m) |                    ▁▇▇▇▇▇▇▇▇▇▇▇▇▇▂             |
2021-09-11 (Sat):  00h00m
2021-09-12 (Sun):  00h00m
2021-09-13 (Mon):  08h26m ( 00h56m) |                    ▃▇▇▇▅▂▇▇▇▇▇▇▇▇▇▇▅▇▇▃        |
2021-09-14 (Tue):  08h07m ( 00h37m) |                    ▁▇▇▇▇▆▇▇▇▇▇▇▇▇▁▆▇▇▇▂▁       |
2021-09-15 (Wed):  08h56m ( 01h26m) |                      ▁▆▇▇▇▇▇▇▇▇▇▇▅▇▅▇▇▇▄   ▆▅  |
2021-09-16 (Thu):  08h08m ( 00h38m) |                    ▁▇▇▇▇▇▇▇▇▇▇▇▇▇▅▇▇▇          |
2021-09-17 (Fri):  05h03m (-02h26m) |                     ▇▁▂▇▇▇▇▇▇▇▇▇▇▇▂            |
2021-09-18 (Sat):  00h00m ( 00h00m) |                                       ▁        |
2021-09-19 (Sun):  00h51m ( 00h51m) |                                             ▆▁ |
2021-09-20 (Mon):  08h54m ( 01h24m) |    ▇▇▇▁              ▇▆▄▇▇▇▇▇▇▇▇▇▇▇▇▇▇ ▄▂      |
2021-09-21 (Tue):  06h59m (-00h30m) |                       ▅▇▇▇▇▇▆▇▇▇▇▇▇▇▇          |
2021-09-22 (Wed):  08h13m ( 00h43m) |                      ▄▇▇▆▇▇▇▇▇▇▇▆▅▂    ▄▇▇▇▇▆▁▁|
2021-09-23 (Thu):  08h08m ( 00h38m) |                     ▆▇▇▇▇▇▇▇▇▇▇▇▇▇▇▅▂    ▂▇▁   |
2021-09-24 (Fri):  07h30m ( 00h00m) |                     ▃▇▇▇▇▇▇▂▆▇▃▇▇▇▇▇▇▇▃▁▁      |
2021-09-25 (Sat):  02h59m ( 02h59m) |                               ▃            ▄▁▇▇|
2021-09-26 (Sun):  03h22m ( 03h22m) |    ▇▇▇▇▆           ▄▇▄  ▁                      |
2021-09-27 (Mon):  08h13m ( 00h43m) |                    ▂▇▇▇▆▆▇▇▇▇▇▇▇▇▇▆▇▄▄▃        |
2021-09-28 (Tue):  04h53m (-02h36m) |                       ▃▄▇▃▇▇▇▇▇▇▇▅             |
2021-09-29 (Wed):  07h49m ( 00h19m) |                      ▅▇▇▇▆▇▇▇▇▇▂▃▆▆▇▇▅     ▃▇▆ |
2021-09-30 (Thu):  09h39m ( 02h09m) |                     ▄▇▇▇▆▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▅     |
 170h19m total
 05h19m off balance during this period
```

## How it works

I personally use this for tracking work hours.

Each 10 seconds, or for each _tick_, I save a row in a SQLite3 database with
the title of the currently active window on and for how long I've been
inactive.

A tick counts as active time if you have been idle for less then `IDLE_TIME` (I
use 5 min). If I attend a virtual meeting I use slightly higher thresholds, as
virtual meetings tend to lead to some inactivity (from your window managers
point of view).

Post-pandemic feature; IDLE_TIME is ignored for active time if I'm connected to
the office WiFi.

I personally check if Slack is running, as a signal to whether I'm «working» or
not. If i close Slack, i don't register active time. This is configurable.
This has the side effect of making me more mindful about closing work related
programs when I'm actually not working.


## Usage

### Register a tick

    ./wal.py reg

### Stats

    ./way.py stats [--since YYYY-MM-DD] [--limit 20]

## Support

The standard config and implementation does only support Linux and X window
system, but feel free to add support for others, see [this
interface](https://github.com/torvald/TorWAL/blob/main/wal/system.py).

## Installation

Requires python 3.5 or newer.

Only standard python libraries are in use, so no need for virtual envs.

Crontab only have minutes as its smallest unit, and I wanted to collect data
every 10th second. I could make it into a running daemon, but this was just the
simplest way about:

    crontab -e

and add

    # m h  dom mon dow   command
    * * * * * sleep 0; [/path/to/modern/python] /path/to/folder/wal.py reg
    * * * * * sleep 10; [/path/to/modern/python] /path/to/folder/wal.py reg
    * * * * * sleep 20; [/path/to/modern/python] /path/to/folder/wal.py reg
    * * * * * sleep 30; [/path/to/modern/python] /path/to/folder/wal.py reg
    * * * * * sleep 40; [/path/to/modern/python] /path/to/folder/wal.py reg
    * * * * * sleep 50; [/path/to/modern/python] /path/to/folder/wal.py reg

To keep it more accessible i carry this alias in my .bashrc

    alias torwal="/path/to/folder/wal.py"
