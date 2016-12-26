#!/usr/bin/env python
# -*- coding: utf-8 -*-
import httplib
import re

'''
Get shares price from nasdaq.com
>nasdaq [symbol] [percet_limit]
'''

def get_price(symbol, limit):
    symbol = str(symbol)
    limit  = float(limit)

    agent = "Mozilla/5.0; Windows NT 6.1; rv:50.0; Gecko/20100101 Firefox/50.0" 
    headers = {"User-Agent": agent,
                "Accept": "text/html",
                "Accept-Language": "en, en-US",
                "Accept-Charset": "utf-8",
                "Referer": "/"}

    con = httplib.HTTPConnection("www.nasdaq.com")
    con.request("GET", "/symbol/" + symbol, headers=headers)
    try:
        result = con.getresponse()
    except:
        print "No response"
    out = result.read()
    con.close()

    #with open("m.html", 'w') as f:
    #    f.write(out)

    def get_data(out):
        plast = re.compile('<div id="qwidget_lastsale" class="qwidget-dollar">(.*?)</div>')
        pnet  = re.compile('<div id="qwidget_netchange" class="qwidget-cents qwidget-\w+">(.*?)</div>')
        parr  = re.compile('<div id="qwidget-arrow"><div class="marginLR10px arrow-(.*?)"></div></div>')
        pperc = re.compile('<div id="qwidget_percent" class="qwidget-percent qwidget-\w+" style="white-space:nowrap">(.*?)%</div>')
        ptime = re.compile('<span id="qwidget_markettime">(.*?)</span>')

        return plast.findall(out)[0],\
               pnet.findall(out)[0],\
               parr.findall(out)[0],\
               pperc.findall(out)[0],\
               ptime.findall(out)[0]

    lastsale, netchange, arrow, percent, markettime = get_data(out)

    report = """%s: %s
    lastsale: %s 
    netchange: %s
    arrow: %s
    percent: %s
""" % (symbol, markettime, lastsale, netchange, arrow, percent)

    if (float(percent) >= limit):
        print report   
        return report

    return

#get_price("", 0)
