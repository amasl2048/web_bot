from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.static import File
import os, base64
from random import choice
import jabber_ru

from twisted.python import log
log_file = open("static_url.log", "a")
log.startLogging(log_file)

url = base64.encodestring(str(os.urandom(6))).strip()

f = open("myhost.txt", "r")
host = f.readline().strip()
f.close()

port = choice(range(9000,9999))
out = "http://%s:%s/%s/" % (host, port, url)
if out:
    #print out
    jabber_ru.send_xmpp(out)

local_path = "/shared/GC/files"
root = Resource()
root.putChild(url, File(local_path))

factory = Site(root)
reactor.listenTCP(port, factory)
timer_sec = 60 * 60 * 24 * 7 # sec * min * hours * days
reactor.callLater(timer_sec, reactor.stop)
print "Start...", out
reactor.run()
print "Done."
log_file.close()
