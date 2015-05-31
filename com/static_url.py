from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.static import File
import os, base64
from random import choice
import jabber_ru
import yaml
from twisted.python import log
import qrcode

log_file = open("static_url.log", "a")
log.startLogging(log_file)

url = base64.encodestring(str(os.urandom(6))).strip()

url_conf = yaml.load(open("static_url.yml"))
host = url_conf["host"].strip()
local_path = url_conf["local"].strip()

port = choice(range(9000,9999))
out = "http://%s:%s/%s/" % (host, port, url)

img = qrcode.make(out)
img.save(local_path + "url.png", "png")

if out:
    #print out
    jabber_ru.send_xmpp(out)

root = Resource()
root.putChild(url, File(local_path))

factory = Site(root)
reactor.listenTCP(port, factory)
timer_sec = 60 * 60 * 24 * url_conf["days"] # sec * min * hours * days
reactor.callLater(timer_sec, reactor.stop)
print "Start...", out
reactor.run()
print "Done."
log_file.close()
