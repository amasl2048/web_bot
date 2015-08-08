#!/usr/bin/env python
# -*- coding: utf-8 -*-
from com.yahoo_weather import weather_report as weather
from com.rbc_currency import rbc_get as rbc
from com.bbc_news import bbc_rss as bbc
from com.micex import ex_rate as rate
from com.traff import traffic_report as traffic
from com.nasdaq import get_price
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
    out = weather("diff")
elif (key == "rbc_m"):
    out = rbc("m")
elif (key == "rbc_y"):
    out = rbc("y")
elif (key == "bbc"):
    out = bbc("new")
elif (key == "rate"):
    out = rate("changes")
elif (key == "traff"):
    out = traffic("update")
elif (key == "nasdaq"):
    out = get_price(sys.argv[2], sys.argv[3])
else:
    out = ""
    print "No data"

if out:
    jabber_ru.send_xmpp(out)
    print out
