#!/usr/bin/env python
# -*- coding: utf-8 -*-
from jabberbot import JabberBot, botcmd
import datetime
import yaml
import sys, subprocess, re
from com.yahoo_weather import weather_report as weather
from com.rbc_currency import rbc_get as rbc
from com.bbc_news import bbc_rss as bbc
from com.micex import ex_rate as rate

class SystemInfoJabberBot(JabberBot):

    def check_url( self, arg):
        r = re.compile(r"^[a-z0-9_.-]+$")
        if ( (len(arg) < 256) and (r.search(arg.strip())) ):
            return True
        return False
        
    @botcmd
    def serverinfo( self, mess, args):
        """Displays information about the server"""
        version = open('/proc/version').read().strip()
        loadavg = open('/proc/loadavg').read().strip()
        return '%s\n\n%s' % ( version, loadavg, )

    @botcmd
    def uptime( self, mess, args):
        """Displays uptime of the server"""
        p = subprocess.Popen(['uptime', '-p'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        return str(out)

    @botcmd
    def urlinfo( self, mess, args):
        """Displays information from url"""
        if (self.check_url(args)):
            s = str(args).strip()
        else:
            return "Error"
        p = subprocess.Popen(['curl', '-I', s],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        return str(out)

    @botcmd
    def ping( self, mess, args):
        """Ping address"""
        if (self.check_url(args)):
            s = str(args).strip()
        else:
            return "Error"
        p = subprocess.Popen(['ping', '-c 3', s],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        if err: return str(err)
        return str(out)

    @botcmd
    def nslookup( self, mess, args):
        """DNS name look up resolution"""
        if (self.check_url(args)):
            s = str(args).strip()
        else:
            return "Error"
        p = subprocess.Popen(['nslookup', s],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        return str(out)

    @botcmd
    def whois( self, mess, args):
        """Whois adrress service"""
        if (self.check_url(args)):
            s = str(args).strip()
        else:
            return "Error"
        p = subprocess.Popen(['whois', s],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        return str(out)

    @botcmd
    def time( self, mess, args):
        """Displays current server time"""
        return str(datetime.datetime.now())

    @botcmd
    def rot13( self, mess, args):
        """Returns passed arguments rot13'ed"""
        if (len(args) > 255): return "Too long args..."
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

