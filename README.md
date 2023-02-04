# XMPP bot 

`jabber_bot.py` - wait commands from XMPP client and respond with correspondent reply.

`web_bot.py` - periodically runs commands by crontab.

Read configuration filename from `BOT_CFG` environment variable.
Configuration file example:

```yaml
---
debug: False
work_dir: "/home/ubuntu"
log_file: "bot.log"
log: "/var/log/slixbot/slixbot.log"

jabber_bot:
    hash: "xxxxxx"
    salt: "xxxx"

static_url:
    host: "<domain>"
    local: "/shared/pub"
    days: 5

web_server:
    memofile: "/shared/doc/memo.dat"
    linkfile: "/shared/doc/links.dat"

velo:
    debug: False
    csvfile: "/shared/doc/velo.csv"
    work:
       - "0:50" # h:mm
       - "12" # km

bbc:
    rss: "http://feeds.bbci.co.uk/news/rss.xml"
    my_words: "/home/ubuntu/web_bot/my_words.txt"

traff:
    limit: 900 # Mb
    iface:
        - "ens3"
    dat_file: "/home/ubuntu/web_bot/traf_report.yml"

tlog:
       log: "/home/ubuntu/twistd.log"
       counter: "/var/www/<site>/counter.png"

content:
       url: "http://<path>"

ticker:
    api: "https://api.<site>/v1/ticker/"
    tickers:
        - "xxx"
    price: "xxxx"
    lim_24h: 5
    lim_7d: 7

files:
    list:
        - "/var/mail/ubuntu"
```

## Commands:

## `bbc`

RSS news fetcher:
  - read remote .xml
  - find all news corresponding to keywords
  - check old news by md5 hashes
  - send keywords by xmpp (or email)

parameters:

    "all" - all available news
    "new" - only new ones from last check

## `content`

Checking does web content changed

## `erlang`

Erlang B calculator:

- System with losses
- Simple requests stream
- Exponential distribution law of wait time
 
:inputs: BTH (erlangs), Blocking (refusal probability)

:output: Number of lines

erlangs limited upto 1M

```
erlang 10 0.05

(9:13:15 PM): 0.0364969 blocking probability
15 lines
```

## `files`

Check files changes if not zero size

## `fspl`

Rerutn Free-space path loss (FSPL) in dB

    fspl <Mhz> <meters>

```
fspl 1880 100

(9:11:53 PM): 77.9 dB
```

## `nasdaq` (obsolite)

Get shares price from nasdaq.com

>nasdaq [symbol] [percent_limit]

## `notify` and `events`

    notify <cmd> [options]
        cmd:
           "once" <date> <text> - one event at the date
              date: "YYYY-MM-DD"
              text: any content

    events <cmd>
       cmd:
           0        - display today events
           1        - tomorrow events
           week     - list from 0 to 6 days
           nextweek - list from 7 to 13 days
           month    - list from 0 to 31 days
           year
           
           view <YYYY-MM-DD>  - view event raw data from the given date
           del <hash>         - delete event with the hash
           clean <days>       - delete events older than given days

## `packet`

Calculate packet transmission time from given packet size and link rate

packet <size> <rate>

    size: packet size (bytes) - b, k, m, g, t, p (multiply by 1024)
    rate: link rate (bits per sec) - K, M, G, T (multiply by 1000)

```
packet 1500b 100M

(9:21:18 PM): 120.00000000000001 us
```

## `tlog`

- parse twisted log, eval counters
- HTTP status codes stats
- Count search engines requests
- Generate image file from text with counts for web page

## `totp_check`

OTP authentication check

## `traff`

Linux server traffic stats in Mbytes
per week/month

    param:
      today  - only traff data from last update
      update - rewrite traff yml file

```
traff

(9:26:39 PM): ens3	 receive/send Mb
Daily:	 453.7/171.8
Weekly:	 7233.6/3552.4
Monthly:	 4704.3/2955.2
Eth:	 672983.4/275688.9
uptime:  18:26:40 up 603 days, 21:56,  1 user,  load average: 0.00, 0.02, 0.00
```

## `velo`

Save received tracking data to csv file:
velo_cmd("add <hh:mm> <km>")

Printing data statistics.

    velo <cmd> <options>
      cmd:  
        "add <h:mm> <km>"  - adding new data to csv
        "date <yyyy-mm-dd> <h:mm> <km>" - adding new data for the date
        "help" - print help
        "stat [year]" - return velo statistics for the year
        "work" - add default time/distance to work
        "top" - the best achievement
        "last" - last item

## `yahoo_weather` (obsolite)

    parameter:
    "all" - full weather report
    "diff" - only difference from last report

```
---
date: %s
temp_h: %s
temp_l: %s
condition: %s
humidity: %s
pressure: %s
chill: %s
speed: %s
```
