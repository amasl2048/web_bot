#!/usr/bin/env python
# -*- coding: utf-8 -*-
from jabberbot import JabberBot, botcmd
import datetime
import yaml
import sys, subprocess, re
import hashlib
from com.yahoo_weather import weather_report as weather
from com.rbc_currency import rbc_get as rbc
from com.bbc_news import bbc_rss as bbc
from com.micex import ex_rate as rate
from com.totp_check import totp_accept as totpcheck
from com.traff import traffic_report as traffic
from com.velo import velo_cmd as velo

class SystemInfoJabberBot(JabberBot):

    def check_cont(self, mess):
        conf = {
            "hash": "01c05ab45941795a2e99df9cf0c1e79099d875bfe9094cd5a8daedbbd6eedecba2249fc6b1e1b2a82233e22e310f7073a7177253d4dfe2bc725fd71662217f52",
        "salt": "TgmHli0e+J3rkmUA"
            }
        who = mess.getFrom().getStripped()
        m = hashlib.sha512()
        m.update(who)
        m.update(conf["salt"])

        if (conf["hash"] == m.hexdigest()):
            return True
        else:
            print who
            #print m.hexdigest()
            return False

    def check_url( self, arg):
        r = re.compile(r"^[a-z0-9_.-]+$")
        if ( (len(arg) < 256) and (r.search(arg.strip())) ):
            return True
        return False

    def check_cmd( self, arg):
        r = re.compile(r"^[a-z0-9.:\s]+$")
        if ( (len(arg) < 256) and (r.search(arg.strip())) ):
            return True
        return False
 
    @botcmd
    def whoami(self, mess, args):
        """Tells you your username"""
        return mess.getFrom().getStripped()

    @botcmd
    def time( self, mess, args):
        """Displays current server time"""
        if not self.check_cont(mess): return "Error"
        return str(datetime.datetime.now())

    @botcmd
    def totp( self, mess, args):
        """Check TOTP auth"""
        if not self.check_cont(mess): return "Error"
        if totpcheck(args): return "ok"
        return "error"

    @botcmd
    def traff( self, mess, args):
        """Traffic data from last update"""
        if not self.check_cont(mess): return "Error"
        return str(traffic("today"))

    @botcmd
    def serverinfo( self, mess, args):
        """Displays information about the server"""
        if not self.check_cont(mess): return "Error"
        version = open('/proc/version').read().strip()
        loadavg = open('/proc/loadavg').read().strip()
        return '%s\n\n%s' % ( version, loadavg, )

    @botcmd
    def uptime( self, mess, args):
        """Displays uptime of the server"""
        if not self.check_cont(mess): return "Error"
        p = subprocess.Popen(['uptime', '-p'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        return str(out)

    @botcmd
    def urlinfo( self, mess, args):
        """Displays information from url"""
        if not self.check_cont(mess): return "Error"
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
        if not self.check_cont(mess): return "Error"
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
        if not self.check_cont(mess): return "Error"
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
        if not self.check_cont(mess): return "Error"
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
    def share( self, mess, args):
        """share <dir> <days>"""
        if not self.check_cont(mess): return "Error"
        if len(args) == 0:
            s = ""
        elif self.check_cmd(args):
            s = str(args).strip()
        else:
            return "Error"
        cmd = []
        cmd.append("./static_url.py")
        cmd += s.split()
        cmd.append("&")
        #print cmd
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        #out, err = p.communicate()
        return "Done."

    @botcmd
    def rot13( self, mess, args):
        """Returns passed arguments rot13'ed"""
        if not self.check_cont(mess): return "Error"
        if (len(args) > 255): return "Too long args..."
        return args.encode('rot13')

    @botcmd
    def weather( self, mess, args):
        """Displays weather forcast from yahoo"""
        if not self.check_cont(mess): return "Error"
        return str(weather("all"))

    @botcmd
    def bbc( self, mess, args):
        """Displays news from BBC rss feed"""
        if not self.check_cont(mess): return "Error"
        return str(bbc("all"))

    @botcmd
    def rate( self, mess, args):
        """Displays MICEX USD and EUR to RUR ex-rates"""
        if not self.check_cont(mess): return "Error"
        return str(rate("all"))

    @botcmd
    def rbc( self, mess, args):
        """Displays CBRF currency ex-rate from RBC"""
        if not self.check_cont(mess): return "Error"
        return str(rbc("m"))

    @botcmd
    def velo( self, mess, args):
        """Displays velo statistics"""
        if not self.check_cont(mess): return "Error"
        if len(args) == 0:
            return str(velo("stat"))
        elif self.check_cmd(args):
            s = str(args).strip()
            #print s
        else:
            return "Error"
        return str(velo(s))

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

