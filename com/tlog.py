#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pandas import read_csv
import time
import yaml
from PIL import Image, ImageDraw, ImageFont
import StringIO
'''
parse twistd log
'''

import common
csvfile = common.config["tlog"]["log"]
imgfile = common.config["tlog"]["counter"]

today = time.strftime("%Y-%m-%d")

def mkimg(txt, imgfile):
    img = Image.new("RGB", (250,30), "white")

    font = ImageFont.load_default()
    draw = ImageDraw.Draw(img)
    draw.text((10,10), txt, font=font, fill="black")

    #img.show()
    img.save(imgfile)

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
    #import ipdb; ipdb.set_trace()
    #today = "2017-02-24"
    try:
        td = df.loc[today]
    except:
        return "Empty"

    hits = td.shape[0]
    hosts = td[3].unique().shape[0]

    txt = "%s hits: %s, hosts: %s" % (today, hits, hosts) 

    gb = td[td[12] == 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'].shape[0] # user-agent
    gi = td[td[12] == 'Googlebot-Image/1.0'].shape[0]
    ya = td[td[12] == 'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)'].shape[0]
    yi = td[td[12] == 'Mozilla/5.0 (compatible; YandexImages/3.0; +http://yandex.com/bots)'].shape[0]

    err = td[td[9] > 304][8].shape[0] # error http code

    bots = 'google-bot: %s, google-img: %s, yandex-bot: %s, yandex-img: %s' % (gb, gi, ya, yi)
    views = 'views: %s, errors: %s' % (hits - gb - gi - ya - yi, err)
    report = "%s\n %s\n %s" % (txt, bots, views)

    if arg == "today":
        mkimg(txt, imgfile)
        return report

    if arg == "error":
        return td[td[9] > 304][8].unique() # error requests

    if arg == "warning":
        return wrn 

    return report

#print tcount("error")
