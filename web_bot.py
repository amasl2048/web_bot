#!/usr/bin/env python
# -*- coding: utf-8 -*-

from com import *
import re
import time
import sys
import subprocess

try:
    key = sys.argv[1]
except:
    print '''Usage: web_bot.py [command]
    command:
        weather - forcast from yahoo in difference to last.yml file
        rbc_m - CBRF currency rates from RBC (monthly stats) 
        rbc_y - CBRF currency rates from RBC (yearly stats) 
        bbc - news from BBC rss feed by keywords from my_words.txt
        rate - last ex-rates changes from MICEX
        nasdaq [symbol] [percent_limit] - get share price from NASDAQ
        ticker - change
        velo - stat
        files - files change check
        events - display planned events
'''
    sys.exit(0)

if (key == "test"):
    out = "test"
elif (key == "weather"):
    out = yahoo_weather.weather_report("diff")

elif (key == "rbc_m"):
    out = rbc_currency.rbc_get("m")
elif (key == "rbc_y"):
    out = rbc_currency.rbc_get("y")

elif (key == "bbc"):
    out = bbc_news.bbc_rss("new")

elif (key == "rate"):
    out = micex.ex_rate("changes")
elif (key == "traff"):
    out = traff.traffic_report("update")
elif (key == "nasdaq"):
    out = nasdaq.get_price(sys.argv[2], sys.argv[3])

elif (key == "counter"):
    out = tlog.tcount("today")
elif (key == "content"):
    out = content.content_cmd()

elif (key == "ticker"):
    out = ticker.ticker_cmd("change")

elif (key == "files"):
    out = files.files_cmd()

elif (key == "velo"):
    report = velo.velo_cmd("stat")
    pattern = re.compile("Last:.(\d+).days")
    try: 
        last = int(pattern.findall(report)[0])
    except:
        last = 0
    mon = time.localtime().tm_mon
    if (mon > 3) and (mon < 11):
        velotime = True
    else:
        velotime = False
    if (last > 3) and velotime:
        out = report
    else:
        out = ""

elif (key == "events_today"):
    when, report = notify.get_event(0)
    if report:
        out = "%s %s" % (when, report)
elif (key == "events_tomorrow"):
    when, report = notify.get_event(1)
    if report:
        out = "%s %s" % (when, report)
elif (key == "events_3days"):
    when, report = notify.get_event(3)
    if report:
        out = "%s %s" % (when, report)
elif (key == "events_week"):
    when, report = notify.get_event(7)
    if report:
        out = "%s %s" % (when, report)
    
else:
    out = ""
    print "No data"

if out:
    p = subprocess.Popen(['./xsend.py', out],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    output, err = p.communicate()
    print output, err

print out
