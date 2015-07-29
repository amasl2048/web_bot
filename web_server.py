#!/usr/bin/python
# -*- coding: utf-8 -*-
import pyelliptic
import getpass
import base64

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import ssl
from twisted.python.modules import getModule

import sys, os, time
import urlparse
import urllib
import yaml

import subprocess
import pprint

from link_server import Link
from memo_server import Memo

debug = True

def load_config(bot_config):
    global debug
    print "\nReading config..."
    config = yaml.load( open(bot_config))
    log_file = os.path.join(config["work_dir"], config["log_file"])
    sys.stdout = open(log_file, "a")

    #debug = config["debug"]
    if debug:
        from twisted.python import log
        log.startLogging(sys.stdout)

    memo_file = os.path.join(config["work_dir"], config["web_server"]["memofile"])
    link_file = os.path.join(config["work_dir"], config["web_server"]["linkfile"])

    if not os.path.isfile(memo_file):
        print "No file: ", memo_file
        sys.exit(0)

    if not os.path.isfile(link_file):
        print "No file: ", link_file
        sys.exit(0)
    return memo_file, link_file

class Psw:
    password = ""
    status = ""

class WebData:
    reply = '''<html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    </head>
        <body>%s</body>
</html>
'''

    form = '''<html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    </head>
        <body><form method="POST"><input name="add" type="text" /></form></body>
</html>
'''
    def __init__(self, myfile):
        self.my_file = myfile
        #self.keypass = Psw.password

    def show_decr(self):
        print "\nDecrypting..."
        ctext = ""
        with open(self.my_file, "r") as f:
            iv = base64.b64decode(f.readline().strip())
            for line in f:
                ctext += line

        ctx2 = pyelliptic.Cipher(Psw.password, iv, 0, ciphername='bf-cfb')
        try:
            Psw.status = "\nOK\n"
            return unicode(ctx2.ciphering(base64.b64decode(ctext)), "utf-8")
        except:
            time.sleep(1)
            Psw.status = "\nFail\n"
            print "Error: wrong pass \"%s\"" % Psw.password


class DataCmd(Resource):
    isLeaf = True

    def __init__(self, memo_file):
        self.Data = WebData(memo_file)
        
    def render_POST(self, request):
        global debug
        newdata = request.content.getvalue()
        try:
            decode = urlparse.parse_qs(newdata)
        except:
            return "\nError: decode..\n"
        if debug:
            #pprint.pprint(decode)
            pass

        if decode.keys()[0] == "psw":
            Psw.password = decode["psw"][0]
            if self.Data.show_decr():
                Psw.status = "\nOK\n"
            return Psw.status

        if decode.keys()[0] == "status":
            if not Psw.password:
                Psw.status = "Running.."
            return Psw.status
        
        elif decode.keys()[0] == "stop":
            print "\nStop reactor..\n"
            reactor.stop()


class DataMemo(Resource, Memo):
    isLeaf = True
    def __init__(self, memo_file):
        self.memofile = memo_file
        self.Data = WebData(memo_file)
    
    def render_GET(self, request):
        return self.Data.form

    def render_POST(self, request):
        #pprint(request.__dict__)
        global debug
        out = self.Data.show_decr()
        if out:
            self.memo_data = out
        else:
            return self.Data.reply % ""
        
        newdata = request.content.getvalue()
        try:
            decode = urlparse.parse_qs(newdata)
        except:
            return self.Data.reply % "Error: decode.."
        if debug:
            pprint.pprint(decode)

        if decode.keys()[0] == "add":
            self.memo_add(self.memofile, unicode(decode["add"][0], "utf-8"), Psw.password, self.memo_data)
            self.memo_data = self.Data.show_decr()
            return self.Data.reply % "Done."

        elif decode.keys()[0] == "del":
            out = self.memo_del(self.memofile, decode["del"][0].upper(), Psw.password, self.memo_data)
            if not out:
                return self.Data.reply % "None"
            self.memo_data = self.Data.show_decr()
            return self.Data.reply % out.encode("utf-8")
        
        elif decode.keys()[0] == "show":
            return self.Data.reply % self.memo_data.encode("utf-8")
        
        elif decode.keys()[0] == "clear":
            self.memo_clear(self.memofile, Psw.password)
            self.memo_data = "---\n"
            return self.Data.reply % "Clear"
        
        elif decode.keys()[0] == "stat":
            return self.Data.reply % len(yaml.load(self.memo_data).keys())

        return self.Data.reply % "Error: key.."
       
class DataLink(Resource, Link):
    isLeaf = True
    def __init__(self, link_file):
        self.linkfile = link_file
        self.Data = WebData(link_file)

    def render_POST(self, request):
        global debug
        out = self.Data.show_decr()
        if out:
            self.link_data = out
        else:
            return self.Data.reply % ""
        
        newdata = request.content.getvalue()
        try:
            decode = urlparse.parse_qs(newdata)
        except:
            return self.Data.reply % "Error: decode.."
        if debug:
            pprint.pprint(decode)

        if decode.keys()[0] == "stat":
            return self.Data.reply % self.link_stat(self.link_data).encode("utf-8")

        elif decode.keys()[0] == "add":
            carg = decode["add"][0].split()
            out = self.Data.reply % self.link_add(self.linkfile, Psw.password, self.link_data, unicode(carg[0], "utf-8"), unicode(carg[1], "utf-8")).encode("utf-8")
            self.link_data = self.Data.show_decr() # 2
            return out

        elif decode.keys()[0] == "show":
            return self.Data.reply % self.link_data.encode("utf-8")

        elif decode.keys()[0] == "del":
            return self.Data.reply % self.link_del(self.Data.link_data, decode["del"][0]).encode("utf-8")

        elif decode.keys()[0] == "tag":
            return self.Data.reply % self.link_tag(self.link_data, unicode(decode["tag"][0], "utf-8")).encode("utf-8")

        elif decode.keys()[0] == "url":
            return self.Data.reply % self.link_url(self.link_data, unicode(decode["url"][0], "utf-8")).encode("utf-8")
        
        elif decode.keys()[0] == "title":
            return self.Data.reply % self.link_title(self.link_data, unicode(decode["title"][0], "utf-8")).encode("utf-8")
        
        elif decode.keys()[0] == "search":
            return self.Data.reply % self.link_search(self.link_data, unicode(decode["search"][0], "utf-8")).encode("utf-8")
        
        return self.Data.reply % "Error: key.."

def run_reactor():
    print "\nRun reactor..."
    memo_file, link_file = load_config("/etc/bot.config")
    
    os.chdir("/etc")
    certData = getModule(__name__).filePath.sibling("client01.pem").getContent()
    certificate = ssl.PrivateCertificate.loadPEM(certData)

    root = Resource()
    root.putChild("cmd",  DataCmd(memo_file))
    root.putChild("memo", DataMemo(memo_file))
    root.putChild("link", DataLink(link_file))
    factory = Site(root)
    reactor.listenSSL(8880, factory, certificate.options(), interface="127.0.0.1")
    reactor.run()

def start():
    subprocess.Popen(["python", "web_server.py", "daemon", "&"])

def stop():
    data = urllib.urlencode({"stop": "server"})
    url = "https://localhost:8880/cmd"
    try:
        urllib.urlopen(url, data)
    except IOError:
        return

def status():
    data = urllib.urlencode({"status": "server"})
    url = "https://localhost:8880/cmd"
    res = urllib.urlopen(url, data)
    print res.read()
    res.close()

def psw():
    if len(sys.argv) == 3: 
        passwd = sys.argv[2] # this could be displayed in shell history!
    else:
        passwd = getpass.getpass() # secure input
    data = urllib.urlencode({"psw": passwd})
    url = "https://localhost:8880/cmd"
    res = urllib.urlopen(url, data)
    print res.read()
    res.close()

def run():
    if sys.argv[1] == "start":
        start();
    elif sys.argv[1] == "stop":
        stop();
    elif sys.argv[1] == "restart":
        stop();
        start();
    elif sys.argv[1] == "psw":
        psw()
    elif sys.argv[1] == "status":
        status()
    elif sys.argv[1] == "daemon":
         run_reactor();
    else:
        print("Unknown: ", sys.argv[1])


### MAIN
if len(sys.argv) > 1:
    run()
else:
    print("Run with option: start | stop");
