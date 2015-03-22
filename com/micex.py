#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, httplib
from datetime import date
from numpy import genfromtxt
from StringIO import StringIO
from time import asctime
'''
Get currency rates from micex.ru
  - send results over xmpp
'''
def ex_rate(par):
    '''
    par:
    "all" - send recieved data
    "changes" - send only if rate chaged more than 3%
    '''
    today = date.today()

    tickers = ["EUR_RUB__TOM", "USD000UTSTOM"]
    dat = {"EUR_RUB__TOM": {"rate": [], "time": [], "change": []},
           "USD000UTSTOM": {"rate": [], "time": [], "change": []}
           }

    agent = "Mozilla/5.0; Windows NT 6.1; rv:34.0; Gecko/20100101 Firefox/34.0" 
    srv = "www.micex.ru"
    headers = {"User-Agent": agent,
                "Accept": "text/html, text/plain, application/xml",
                "Accept-Language": "ru, ru-RU",
                "Accept-Charset": "utf-8",
                "Referer": "/"}

    def get_data(source, tic):
        '''
        Get csv data
        '''
        arr = urllib.urlencode({"boardid": source, "secid" : tic})
        url = "/issrpc/marketdata/currency/selt/daily/short/result_" +\
        str(today.year) + "_" + today.strftime("%m") + "_" + today.strftime("%d") +\
        ".csv?%s" % arr
        #print url
        con.request("GET", url, headers=headers)
        result = con.getresponse()
        out = result.read()
        #print out
        rate = genfromtxt(StringIO(out), delimiter=";", skip_header = 1, usecols=(8,) )
        td = genfromtxt(StringIO(out), delimiter=";", skip_header = 1, dtype = "S20", usecols=(16,) )
        chg = genfromtxt(StringIO(out), delimiter=";", skip_header = 1, usecols=(3,) )
        return rate, td, chg

    con = httplib.HTTPConnection(srv)

    report = ""
    send = False
    for t in tickers:
        dat[t]["rate"], dat[t]["time"], dat[t]["change"] = get_data("CETS", t)
        if ( (dat[t]["change"] >= 3) or (dat[t]["change"] <= -3) ): send = True

    con.close()

    for t in tickers:
        report += """%s:
    rate: %s 
    time: %s
    change: %s
""" % (t, dat[t]["rate"], dat[t]["time"], dat[t]["change"] )

    if (par == "changes"):
        if (not send): report = ""

    if report:
	print asctime()
	print report   
   
    return report

#ex_rate("all")


