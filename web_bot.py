#!/usr/bin/env python
# -*- coding: utf-8 -*-

from com import *
import jabber_ru

import sys

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
'''
    sys.exit(0)

if (key == "weather"):
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
else:
    out = ""
    print "No data"

if out:
    jabber_ru.send_xmpp(out)
    print out
