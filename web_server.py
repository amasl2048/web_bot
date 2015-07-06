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

import sys, os
import urlparse
import yaml

from link_server import *
from memo_server import *

debug = False
if debug:
    from twisted.python import log
    import pprint
    log.startLogging(sys.stdout)

memofile = "./memo.yml"
if os.path.isfile(memofile) and os.path.isfile(memofile + ".iv"):
    keypass = getpass.getpass()
else:
    print "No file: ", memofile
    sys.exit(0)

linkfile = "./links.yml"
if os.path.isfile(linkfile) and os.path.isfile(linkfile + ".iv"):
    pass
else:
    print "No file: ", linkfile
    sys.exit(0)

def show_decr(myfile, key):
    ### decryption
    ctext = ""
    with open(myfile + ".iv", "r") as f:
        iv = base64.b64decode(f.readline())
    for line in open(myfile, "r"):
        ctext += line

    ctx2 = pyelliptic.Cipher(key, iv, 0, ciphername='bf-cfb')
    try:
        return unicode(ctx2.ciphering(base64.b64decode(ctext)), "utf-8")
    except:
        print "Error"
        sys.exit(0)

memo_data = show_decr(memofile, keypass)
link_data = show_decr(linkfile, keypass)
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

class DataMemo(Resource):
    isLeaf = True
    def render_GET(self, request):
        return form

    def render_POST(self, request):
        global memo_data, keypass, memofile
        #pprint(request.__dict__)
        newdata = request.content.getvalue()
        try:
            decode = urlparse.parse_qs(newdata)
        except:
            return reply % "Error: decode.."
        if debug:
            pprint.pprint(decode)

        if decode.keys()[0] == "add":
            memo_add(memofile, unicode(decode["add"][0], "utf-8"), keypass, memo_data)
            memo_data = show_decr(memofile, keypass) #
            return reply % "Done."
        elif decode.keys()[0] == "show":
            return reply % memo_data.encode("utf-8")
        elif decode.keys()[0] == "clear":
            memo_clear(memofile, keypass)
            memo_data = "---\n"
            return reply % "Clear"
        elif decode.keys()[0] == "stat":
            return reply % len(yaml.load(memo_data).keys())

        return reply % "Error: key.."
       
class DataLink(Resource):
    isLeaf = True

    def render_POST(self, request):
        global link_data, keypass, linkfile
        #pprint(request.__dict__)
        newdata = request.content.getvalue()
        try:
            decode = urlparse.parse_qs(newdata)
        except:
            return reply % "Error: decode.."
        if debug:
            pprint.pprint(decode)

        if decode.keys()[0] == "stat":
            return reply % link_stat(link_data).encode("utf-8")

        elif decode.keys()[0] == "add":
            carg = decode["add"][0].split()
            out = reply % link_add(linkfile, keypass, link_data, unicode(carg[0], "utf-8"), unicode(carg[1], "utf-8")).encode("utf-8")
            link_data = show_decr(linkfile, keypass) # 2
            return out

        elif decode.keys()[0] == "show":
            return reply % link_data.encode("utf-8")

        elif decode.keys()[0] == "del":
            return reply % link_del(link_data, decode["del"][0]).encode("utf-8")

        elif decode.keys()[0] == "tag":
            return reply % link_tag(link_data, unicode(decode["tag"][0], "utf-8")).encode("utf-8")

        elif decode.keys()[0] == "url":
            return reply % link_url(link_data, unicode(decode["url"][0], "utf-8")).encode("utf-8")
        
        elif decode.keys()[0] == "title":
            return reply % link_title(link_data, unicode(decode["title"][0], "utf-8")).encode("utf-8")
        
        elif decode.keys()[0] == "search":
            return reply % link_search(link_data, unicode(decode["search"][0], "utf-8")).encode("utf-8")
        
        return reply % "Error: key.."

      
certData = getModule(__name__).filePath.sibling('client01.pem').getContent()
certificate = ssl.PrivateCertificate.loadPEM(certData)

root = Resource()
root.putChild("memo", DataMemo())
root.putChild("link", DataLink())
factory = Site(root)
reactor.listenSSL(8880, factory, certificate.options(), interface="127.0.0.1")

if __name__ == '__main__':
    reactor.run()

