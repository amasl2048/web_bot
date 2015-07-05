#!/usr/bin/python
# -*- coding: utf-8 -*-
import pyelliptic
import getpass
import base64

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource

import sys, os
from twisted.internet import ssl
from twisted.python.modules import getModule

import urlparse
import shutil, datetime
import yaml

debug = False
if debug:
    from twisted.python import log
    import pprint
    log.startLogging(sys.stdout)

ymlfile = "./memo.yml"
if os.path.isfile(ymlfile) and os.path.isfile(ymlfile + ".iv"):
    keypass = getpass.getpass()
else:
    print "No file: ", ymlfile
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

data = show_decr(ymlfile, keypass)
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

def note_save(myfile, note):
    iv = pyelliptic.Cipher.gen_IV('bf-cfb')
    bi = base64.encodestring(iv)
    ctx = pyelliptic.Cipher(keypass, iv, 1, ciphername='bf-cfb')

    ciphertext = ctx.update(data.encode("utf-8"))
    ciphertext += ctx.final()
    ctext = base64.encodestring(ciphertext)

    shutil.copy2(myfile, myfile + "~")
    shutil.copy2(myfile + ".iv", myfile + ".iv~")
    with open(myfile, "w") as f:
        f.write(ctext) 
    with open(myfile + ".iv", "w") as f:
        f.write(bi)
    return

def note_add(myfile, note):
    """
    Add data to yml file
    """
    global keypass, data
    today = datetime.date.today()
    note_id = base64.b32encode(str(os.urandom(3))).strip()[:5] # first 5 chars

    record = u'''%s:
    date: %s
    note: %s
''' % (note_id, today, note)
    data += record
    note_save(myfile, data)
    return 

def note_clear(myfile):
    """
    Add data to yml file
    """
    global keypass, data

    data = "---\n"
    note_save(myfile, data)
    return

class DataPage(Resource):
    isLeaf = True
    def render_GET(self, request):
        return form

    def render_POST(self, request):
        #pprint(request.__dict__)
        newdata = request.content.getvalue()
        try:
            decode = urlparse.parse_qs(newdata)
        except:
            return reply % "Error: decode.."
        if debug: pprint.pprint(decode)

        if decode.keys()[0] == "add":
            note_add(ymlfile, unicode(decode["add"][0], "utf-8"))
            return reply % "Done."
        elif decode.keys()[0] == "show":
            return reply % (data.encode("utf-8"),)
        elif decode.keys()[0] == "clear":
            note_clear(ymlfile)
            return reply % "Clear"
        elif decode.keys()[0] == "stat":
            return reply % len(yaml.load(data).keys())

        return reply % "Error: key.."
       
      
certData = getModule(__name__).filePath.sibling('client01.pem').getContent()
certificate = ssl.PrivateCertificate.loadPEM(certData)

root = Resource()
root.putChild("memo", DataPage())
factory = Site(root)
reactor.listenSSL(8880, factory, certificate.options(), interface="127.0.0.1")

if __name__ == '__main__':
    reactor.run()

