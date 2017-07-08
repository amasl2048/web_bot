#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
parse twistd log
'''
import time
import StringIO
from pandas import read_csv

from PIL import Image, ImageDraw, ImageFont

import common
csvfile = common.config["tlog"]["log"]
imgfile = common.config["tlog"]["counter"]

today = time.strftime("%Y-%m-%d")


def mkimg(txt, fig):
    '''Generate image file from text'''
    img = Image.new("RGB", (250, 30), "white")

    font = ImageFont.load_default()
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), txt, font=font, fill="black")

    #img.show()
    img.save(fig)


def http_views(data, hit, error):
    '''Count search engins requests'''

    gbot = data == 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'  # user-agent
    gb = gbot[gbot == True].size

    gimg = data == 'Googlebot-Image/1.0'
    gi = gimg[gimg == True].size

    yabot = data == 'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)'
    ya = yabot[yabot == True].size

    yaimg = data == 'Mozilla/5.0 (compatible; YandexImages/3.0; +http://yandex.com/bots)'
    yi = yaimg[yaimg == True].size

    bots = 'google-bot: %s, google-img: %s, yandex-bot: %s, yandex-img: %s' % (gb, gi, ya, yi)
    views = 'errors: %s, views: %s' % (error, hit - gb - gi - ya - yi - error)

    return "%s\n %s\n" % (bots, views)


def http_status(data):
    '''HTTP status codes stats'''

    CODES = [[100, 200],
             [200, 300],
             [300, 400],
             [400, 500],
             [500, 600]]

    RESULTS = {"100": "Info",
               "200": "Success",
               "300": "Redirection",
               "400": "Client errors",
               "500": "Server errors"
               }

    out = "Codes: %s (%s)\n" % (data.size, data.unique())

    acn = 0
    for s1, s2 in CODES:
        scode = data[data >= s1] < s2
        sn = scode[scode == True].size
        acn += sn
        out += "%s %s: %s\n" % (s1, RESULTS[str(s1)], sn)

    out += "errors: %s" % str(data.size - acn)

    return out


def tcount(arg):
    '''parse twisted log, eval counters'''

    csv = ""
    wrn = ""
    for ln in open(csvfile, "r"):
        if not ("Warning:" in ln):
            csv = csv + ln
        else:
            wrn = wrn + ln

    df = read_csv(StringIO.StringIO(csv),
                  sep=' ',
                  header=None,
                  index_col=0,
                  parse_dates=[0],
                  error_bad_lines=False)


    #today = "2017-02-24"
    try:
        td = df.loc[today]
    except:
        return "Empty"

    hits = td.shape[0]
    hosts = td[3].unique().shape[0]

    txt = "%s hits: %s, hosts: %s" % (today, hits, hosts)

    err = td[td[9] > 304][8].shape[0] # error http code

    stats = http_status(td[9])
    bots = http_views(td[12], hits, err)

    report = "%s\n %s\n" % (txt, bots)
    report += stats

    if arg == "today":
        mkimg(txt, imgfile)
        return report

    if arg == "error":
        return td[td[9] > 304][8].unique() # error requests

    if arg == "warning":
        return wrn

    return report

#print tcount("")
