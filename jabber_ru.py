#!/usr/bin/python
import sys
import xmpp
import yaml

def send_xmpp(message):

    Conf = yaml.load(open("/etc/jabber_ru.yml"))

    try:
        jid = xmpp.protocol.JID(Conf["username"])
        jabber = xmpp.Client(jid.getDomain(), debug=[])
        jabber.connect(server=(jid.getDomain(), 5222) )
        jabber.auth(jid.getNode(), Conf["password"])

        jabber.send(xmpp.Message(Conf["contact"], message.strip()))

    except Exception, exc:
        sys.exit( "xmpp failed; %s" % str(exc) ) # give a error message
