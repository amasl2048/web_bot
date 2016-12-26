#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pandas import read_csv
import time
import yaml
from PIL import Image, ImageDraw, ImageFont
'''
parse twistd log
'''

def tcount(arg):
    '''parse twisted log, eval counters'''
    config = yaml.load(open("/etc/bot.config"))
    csvfile = config["tlog"]["log"]

    df = read_csv(csvfile, sep=' ', header=None, index_col=0, parse_dates=[0],
                  error_bad_lines=False)
    today = time.strftime("%Y-%m-%d")
    ##today = "2016-02-07"
    td = df.loc[today]
    hits = td.shape[0]

    hosts = td[3].unique().shape[0]

    img = Image.new("RGB", (250,30), "white")
    txt = "%s hits: %s, hosts: %s" % (today, hits, hosts) 
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(img)
    draw.text((10,10), txt, font=font, fill="black")

    #img.show()
    img.save(config["tlog"]["counter"])

    gi = td[td[12] == 'Googlebot-Image/1.0'].shape[0] # user-agent
    ya = td[td[12] == 'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)'].shape[0]
    yi = td[td[12] == 'Mozilla/5.0 (compatible; YandexImages/3.0; +http://yandex.com/bots)'].shape[0]
    err = td[td[9] > 304][8].shape[0] # error http code

    bots = 'google-img: %s, yandex-bot: %s, yandex-img: %s' % (gi, ya, yi)
    views = 'views: %s, errors: %s' % (hits - gi - ya - yi, err)
    report = "%s\n %s\n %s" % (txt, bots, views)

    if arg == "today":
        return report

    if arg == "error":
        return td[td[9] > 304][8].unique() # error requests 
        
    return report

#print tcount("error")
