#!/usr/bin/env python
# -*- coding: utf-8 -*-
from jabberbot import JabberBot, botcmd
import datetime
import yaml, os
import sys, subprocess, re
import hashlib
import urllib
import logging

from com import *

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
#sys.stdout = open(log_file, "a")

def prnt_log(msg):
    with open(log_file, "a") as f:
        f.write(datetime.datetime.now().isoformat(" ") + " " + msg + "\n")

logging.basicConfig(filename=config["log"], level=logging.ERROR)

def run_jabber():
    prnt_log("### Jabber bot is running...")
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
                prnt_log(who)
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
            r = re.compile(u"^[0-9a-zA-Zа-яА-Я.:/\s-]+$" )
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
            if totp_check.totp_accept(args): return "ok"
            return "error"

        @botcmd
        def cmd( self, mess, args):
            """
            Control jabber service: cmd <>
            stop
            status (return web_server "Running" or "OK")
            """
            if not self.check_cont(mess): return "Error"
            if args.strip() == "stop":
                prnt_log("### Jabber bot is stoping...")
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
            return str(traff.traffic_report("today"))

        @botcmd
        def counter( self, mess, args):
            """Twisted log counter"""
            #print type(args), args
            if not self.check_cont(mess): return "Error"
            if (self.check_url(args)) or args == "":
                s = str(args).strip()
            else:
                return "error"
            return str(tlog.tcount(s))

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
            out, err = p.communicate()
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
            return str(yahoo_weather.weather_report("all"))

        @botcmd
        def bbc( self, mess, args):
            """Displays news from BBC rss feed"""
            if not self.check_cont(mess): return "Error"
            return bbc_news.bbc_rss("all")

        @botcmd
        def rate( self, mess, args):
            """Displays MICEX USD and EUR to RUR ex-rates"""
            if not self.check_cont(mess): return "Error"
            return str(micex.ex_rate("all"))

        @botcmd
        def coins( self, mess, args):
            """Displays tickers rate"""
            if not self.check_cont(mess): return "Error"
            return str(ticker.ticker_cmd("all"))

        @botcmd
        def files( self, mess, args):
            """Check files change"""
            if not self.check_cont(mess):
                return "Error"
            out = str(files.files_cmd())
            if out:
                return str(files.files_cmd())
            else:
                return "Empty"

        @botcmd
        def rbc( self, mess, args):
            """Displays CBRF currency ex-rate from RBC"""
            if not self.check_cont(mess): return "Error"
            return str(rbc_currency.rbc_get("m"))

        @botcmd
        def nasdaq( self, mess, args):
            """Displays NASDAQ share price for symbol"""
            if not self.check_cont(mess): return "Error"
            if len(args) == 0:
                return "Error"
            elif not self.check_url(args):
                return "Error symbol"
            return str(nasdaq.get_price(args.strip(), 0))

        @botcmd
        def velo( self, mess, args):
            """Displays velo statistics"""
            if not self.check_cont(mess): return "Error mess"
            if len(args) == 0:
                return str(velo.velo_cmd("stat"))
            elif self.check_cmd(args):
                s = str(args).strip()
                #print s
            else:
                return "Error"
            return str(velo.velo_cmd(s))

        @botcmd
        def link( self, mess, args):
            """Manage links"""
            if not self.check_cont(mess): return "Error"
            if len(args) == 0:
                return link.link_cmd("").encode("utf-8")
            elif not self.check_link(args):
                return "Error link"
            else:
                return link.link_cmd(args.strip()).encode("utf-8")

        @botcmd
        def memo( self, mess, args):
            """Save notes"""
            if not self.check_cont(mess): return "Error"
            if len(args) == 0:
                return memo_cli.memo_cmd("").encode("utf-8")
            else:
                return memo_cli.memo_cmd(args.strip()).encode("utf-8")

        @botcmd
        def erlang( self, mess, args):
            """Erlang B calculator"""
            if not self.check_cont(mess): return "Error"
            if len(args) == 0:
                return str(erlang_b.erlang(""))
            elif self.check_cmd(args):
                s = str(args).strip()
                #print s
            else:
                return "Error"
            return str(erlang_b.erlang(s))

        @botcmd
        def fspl( self, mess, args):
            """
            FSPL calculator in dB
            fspl <Mhz> <meters>
            """
            if not self.check_cont(mess): return "Error"
            if len(args) == 0:
                return str(fspl.__doc__)
            elif self.check_cmd(args):
                s = str(args).strip()
                #print s
            else:
                return "Error"
            return str(fspl_calc.fspl(s))

    username = jabber_conf["username"]
    password = jabber_conf["password"]
    bot = SystemInfoJabberBot(username, password)
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
    print("Run with option: start | restart | daemon");

