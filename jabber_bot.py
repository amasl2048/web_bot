#!/usr/bin/env python
# -*- coding: utf-8 -*-
from jabberbot import JabberBot, botcmd
import datetime
import yaml
import sys
from com.yahoo_weather import weather_report as weather
from com.rbc_currency import rbc_get as rbc
from com.bbc_news import bbc_rss as bbc
from com.micex import ex_rate as rate

class SystemInfoJabberBot(JabberBot):
    @botcmd
    def serverinfo( self, mess, args):
        """Displays information about the server"""
        version = open('/proc/version').read().strip()
        loadavg = open('/proc/loadavg').read().strip()

        return '%s\n\n%s' % ( version, loadavg, )

    @botcmd
    def time( self, mess, args):
        """Displays current server time"""
        return str(datetime.datetime.now())

    @botcmd
    def rot13( self, mess, args):
        """Returns passed arguments rot13'ed"""
        return args.encode('rot13')

    @botcmd
    def whoami(self, mess, args):
        """Tells you your username"""
        return mess.getFrom().getStripped()

    @botcmd
    def weather( self, mess, args):
        """Displays weather forcast from yahoo"""
        return str(weather("all"))

    @botcmd
    def bbc( self, mess, args):
        """Displays news from BBC rss feed"""
        return str(bbc("all"))

    @botcmd
    def rate( self, mess, args):
        """Displays MICEX USD and EUR to RUR ex-rates"""
        return str(rate("all"))

    @botcmd
    def rbc( self, mess, args):
        """Displays CBRF currency ex-rate from RBC"""
        return str(rbc("m"))

try:
    Conf = yaml.load(open("/etc/xmpp_ru.yml"))
    username = Conf["username"]
    password = Conf["password"]
except:
    print "Error: no xmpp config file"
    sys.exit(0)
    
bot = SystemInfoJabberBot(username, password)
print "Jabber bot is Running..."
bot.serve_forever()

