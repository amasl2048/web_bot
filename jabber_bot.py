#!/usr/bin/env python
# -*- coding: utf-8 -*-
from jabberbot import JabberBot, botcmd
import datetime
import yaml, os
import sys, subprocess, re
import hashlib
import urllib
from com.yahoo_weather import weather_report as weather
from com.rbc_currency import rbc_get as rbc
from com.bbc_news import bbc_rss as bbc
from com.micex import ex_rate as rate
from com.totp_check import totp_accept as totpcheck
from com.traff import traffic_report as traffic
from com.velo import velo_cmd as velo
from com.erlang_b import erlang
from com.link import link_cmd
from com.memo_cli import memo_cmd
from com.nasdaq import get_price
'''
Jabber bot

'''

# read config
try:
    config      = yaml.load(open("/etc/bot.config"))
    jabber_conf = yaml.load(open("/etc/xmpp_ru.yml"))
except:
    print "Error: no config file"
    sys.exit(0)

log_file = os.path.join(config["work_dir"], config["log_file"]) 
sys.stdout = open(log_file, "a")

def run_jabber():

    class SystemInfoJabberBot(JabberBot):

        def check_cont(self, mess):
            global config
            hsh  = config["jabber_bot"]["hash"]
            salt = config["jabber_bot"]["salt"]
            who = mess.getFrom().getStripped()
            m = hashlib.sha512()
            m.update(who)
            m.update(salt)

            if (hsh == m.hexdigest()):
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

        def check_link( self, arg):
            r = re.compile(u"^[0-9a-zA-Zа-яА-Я.:-/\s]+$" )
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
        def cmd( self, mess, args):
            """
	    Control jabber service: cmd <>
	    stop
	    status
	    """
            if not self.check_cont(mess): return "Error"
            if args.strip() == "stop":
                print "Jabber bot is stoping..."
                sys.exit(0)
            if args.strip() == "status":
                    data = urllib.urlencode({"status": "server"})
                    url = "https://localhost:8880/cmd"
                    try:
                        res = urllib.urlopen(url, data)
                    except:
                        return "no connection"
                    out = res.read()
                    res.close()
                    return out
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
            """share <sub_dir> <days>"""
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
        def nasdaq( self, mess, args):
            """Displays NASDAQ share price for symbol"""
            if not self.check_cont(mess): return "Error"
            if len(args) == 0:
                return "Error"
            elif not self.check_url(args):
                return "Error symbol"
            return str(get_price(args.strip(), 0))

        @botcmd
        def velo( self, mess, args):
            """Displays velo statistics"""
            if not self.check_cont(mess): return "Error mess"
            if len(args) == 0:
                return str(velo("stat"))
            elif self.check_cmd(args):
                s = str(args).strip()
                #print s
            else:
                return "Error"
            return str(velo(s))

        @botcmd
        def link( self, mess, args):
            """Manage links"""
            if not self.check_cont(mess): return "Error"
            if len(args) == 0:
                return link_cmd("").encode("utf-8")
            elif not self.check_link(args):
                return "Error link"
            else:
                return link_cmd(args.strip()).encode("utf-8")

        @botcmd
        def memo( self, mess, args):
            """Save notes"""
            if not self.check_cont(mess): return "Error"
            if len(args) == 0:
                return memo_cmd("").encode("utf-8")
            else:
                return memo_cmd(args.strip()).encode("utf-8")

        @botcmd
        def erlang( self, mess, args):
            """Erlang B calculator"""
            if not self.check_cont(mess): return "Error"
            if len(args) == 0:
                return str(erlang(""))
            elif self.check_cmd(args):
                s = str(args).strip()
                #print s
            else:
                return "Error"
            return str(erlang(s))

    username = jabber_conf["username"]
    password = jabber_conf["password"]
    bot = SystemInfoJabberBot(username, password)
    print "Jabber bot is Running..."
    bot.serve_forever()

def start():
    subprocess.Popen(["python", "jabber_bot.py", "daemon", "&"])

def stop(): # TODO
    pass

def run():
    if sys.argv[1] == "start":
        start();
    elif sys.argv[1] == "stop":
        stop();
    elif sys.argv[1] == "restart":
        stop();
        start();
    elif sys.argv[1] == "daemon":
         run_jabber();
    else:
        print("Unknown: ", sys.argv[1])


### MAIN
if len(sys.argv) > 1:
    run()
else:
    print("Run with option: start | stop");

