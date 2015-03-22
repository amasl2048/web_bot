#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, httplib
from numpy import genfromtxt, mean, std, corrcoef
import sys
from datetime import date
import time
'''
Get currency rates from rbc.ru
  - calculate mean, stdev, correlation for last week, month, year
  - send results over xmpp
'''

def rbc_get(key):
    '''
    key:
    "m" - for month statistics
    "y" - for year stats
    '''
    if (key == "y"): lastdays = 720 # for year statistics
    else: lastdays = 60  

    today = date.today()
    #src = ["cb.0", "selt.0"]
    #cur = ["EUR", "USD"]
    tickers = {"selt.0": ["EUR_RUB__TOM", "USD000UTSTOM"],
               "cb.0": ["EUR", "USD"]
                }
    dat = {"EUR": [], "USD": [], "EUR_RUB__TOM": [], "USD000UTSTOM": []}

    meta = {"m": ["1w", "1m"],
            "y": ["3m", "1y"]}

    agent = "Mozilla/5.0; Windows NT 6.1; rv:34.0; Gecko/20100101 Firefox/34.0"
    srv = "export.rbc.ru"
    headers = {"User-Agent": agent,
                "Accept": "text/html, text/plain, application/xml",
                "Accept-Language": "ru, ru-RU",
                "Accept-Charset": "utf-8",
                "Referer": "/"}

    def get_data(source, tic):
        '''
        Get csv data
        '''
        arr = urllib.urlencode({"period":"DAILY",
        "tickers": tic,
        "d1": "12",
        "m1": "01",
        "y1": "2015",
        "d2": str(today.day),
        "m2": str(today.month),
        "y2": str(today.year),
        "lastdays": str(lastdays),
        "separator": ",",
        "data_format": "BROWSER"})

        url = "/free/" + str(source) + "/free.fcgi?%s" % arr
        con.request("GET", url, headers=headers)
        result = con.getresponse()
        dat[tic] = result.read()

        return

    try:
        con = httplib.HTTPConnection(srv)
    except:
        print "Error: no connection!"
        sys.exit(0)
    
    #for s in tickers.keys():
    s = "cb.0"
    for t in tickers[s]:
        get_data(s, t)

    con.close()

    eur = genfromtxt((c for c in dat["EUR"].split()), delimiter=",", usecols=(5,) )
    eur_dates = genfromtxt((c for c in dat["EUR"].split()), delimiter=",", dtype = "S10", usecols=(1,) )
    usd = genfromtxt((c for c in dat["USD"].split()), delimiter=",", usecols=(5,) )
    usd_dates = genfromtxt((c for c in dat["USD"].split()), delimiter=",", dtype = "S10", usecols=(1,) )

    if (lastdays == 60):
        eur1 = mean(eur[-5:]) # 1w
        eur2 = mean(eur[-10:-5]) # 
        eur3 = mean(eur[-20:]) # 1m
        eur4 = mean(eur[-40:-20]) 
        usd1 = mean(usd[-5:])
        usd2 = mean(usd[-10:-5])
        usd3 = mean(usd[-20:])
        usd4 = mean(usd[-40:-20])

    if (lastdays == 720):
        eur1 = mean(eur[-60:]) # 3m
        eur2 = mean(eur[-120:-60])
        eur3 = mean(eur[-240:]) # 1y
        eur4 = mean(eur[-480:-240])
        usd1 = mean(usd[-60:])
        usd2 = mean(usd[-120:-60])
        usd3 = mean(usd[-240:])
        usd4 = mean(usd[-480:-240])

    def procent(ccur, clast):
        return (ccur - clast) / clast * 100

    arr2 = [eur[-1], eur_dates[-1],
           meta[key][0],
           procent(eur1, eur2),
           std(eur[-lastdays/12:]),
           meta[key][1],
           procent(eur3, eur4),
           std(eur[-lastdays/3:]),
           usd[-1], usd_dates[-1],
           meta[key][0],
           procent(usd1, usd2),
           std(usd[-lastdays/12:]),
           meta[key][1],
           procent(usd3, usd4),
           std(usd[-lastdays/3:]),
           meta[key][1],
           eur3/usd3, procent(eur3/usd3, eur4/usd4),
           meta[key][1],
           corrcoef( eur[-lastdays/3:], usd[-lastdays/3:] )[0,1]
           ] 
    report = '''eur: {0:.2f} {1}
    {2}: {3:.2f}% {4:.2f}
    {5}: {6:.2f}% {7:.2f}
usd: {8:.2f} {9}
    {10}: {11:.2f}% {12:.2f}
    {13}: {14:.2f}% {15:.2f}
cross {16}: {17:.2f} {18:.2f}%
corr {19}: {20:.2f}
'''.format(*arr2)

    if (report):
        print time.asctime()
	print report

    return report

#rbc_get("m")
