# -*- coding: utf-8 -*-
import sys
import io
import xml.etree.cElementTree as ET
import hashlib
import urllib2
import time
import redis

import common
'''
RSS news fetcher
  - read remote .xml
  - find all news corresponding to keywords
  - check old news by md5 hashes
  - send keywords by xmpp (or email)
'''

def bbc_rss(parameter):
    '''
    parameter:
    "all" - all available news
    "new" - only new ones from last check
    '''
    bbc_site = common.config["bbc"]["rss"]
    try:
        url = urllib2.urlopen(bbc_site)
        data = url.read()
        url.close()
    except:
        common.prnt_log("Could not connect... %s" % (bbc_site))
        sys.exit(0)
    
    rdb = redis.Redis(host="localhost", port=6379)

    def prnt_log8(msg):
        '''Loging function with utf-8'''
        with io.open(common.log_file, "a", encoding="utf-8") as f:
            f.write("[%s] %s\n" % (time.strftime("%c"), unicode(msg)))
    
    def txt2set(fl):
        words = []
        try:
            for l in open(fl, 'r'):
                words.append(l.strip())
        except:
            #open(fl, 'w').close()
            #print "Warning: empty file %s is created " % fl
            common.prnt_log("Please add your keywords to %s in one column" % fl)
        return set(words)

    hashes = rdb.smembers("bbcnews")
    rdb.delete("bbcnews")
    my_words = txt2set(common.config["bbc"]["my_words"]) # list of keywords in one column
 
    report = ""
    full_report = time.asctime() + "\n\n"
    root = ET.fromstring(data)

    items = root[0].getchildren()
    for item in items:
        item_children = item.getchildren()
        for item_child in item_children:
            if (item_child.tag == "description"):
                if item_child.text:
                    descr = item_child.text.replace(",", "").replace(".", "").replace(":", "").replace("'s", "").replace("'", "").replace("-", " ").split()
                    set_descr = set(descr)
                else:
                    return
                if (my_words & set_descr):
                    prnt_log8(item_child.text)
                    m = hashlib.md5()
                    m.update(item_child.text.encode("utf-8"))
                    h = m.hexdigest()
                    if (not (h in hashes) ):
                        report += item_child.text + "\n\n"
                    full_report += item_child.text + "\n\n"
                    rdb.sadd("bbcnews", h)
    '''
    if (report):
        print time.asctime()
        print unicode(report, "utf-8").encode("utf-8") # '\xa3' -> £
    '''
    if (parameter == "new"):
        out = report
    else:
        out = full_report

    return out.encode("utf-8")

#print bbc_rss("new")

