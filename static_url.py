#!/usr/bin/python
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.static import File
import os, base64
from random import choice
import jabber_ru
import yaml

import qrcode
import sys
'''
Open web access to local file dir with random url:port
>static_url.py <sub_dir> <days> &

and then send the link over jabber and generate QR-code
'''

# read config
config = yaml.load(open("/etc/bot.config"))
log_file = config["log_file"]
sys.stdout = open(log_file, "a")

debug = config["debug"]
if debug:
    from twisted.python import log
    log.startLogging(open(log_file, "a"))

host =       config["static_url"]["host"].strip()
local_path = config["static_url"]["local"].strip() # default values
days =       config["static_url"]["days"]

url = base64.b32encode(str(os.urandom(10))).strip()

if len(sys.argv) == 4: # becaurse "&" - the 4th argv
    if not sys.argv[1].isalnum(): # "/" and ".." in path is not permitted!
        print "Error", sys.argv[1]
        sys.exit(0)
    local_path = os.path.join(local_path, sys.argv[1])
    if not sys.argv[2].isdigit():
        print "Error", sys.argv[2]
        sys.exit(0)
    days = int(sys.argv[2])

port = choice(range(9000,9999))
out = "http://%s:%s/%s/" % (host, port, url)

if out:
    jabber_ru.send_xmpp(out)
    with open("url.link", "w") as f:
        f.write(out)
    img = qrcode.make(out)
    img.save(os.path.join(local_path, "url.png"), "png")

root = Resource()
root.putChild(url, File(local_path))

factory = Site(root)
reactor.listenTCP(port, factory)
timer_sec = 60 * 60 * 24 * days # stop service after (sec * min * hours * days)
reactor.callLater(timer_sec, reactor.stop)
print "Start...", out, local_path, days
reactor.run()
print "Done."


