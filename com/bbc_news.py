# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import hashlib
import urllib2
import time
import sys
import redis
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
    try:
        url = urllib2.urlopen('http://feeds.bbci.co.uk/news/rss.xml')
        data = url.read()
        url.close()
    except:
        print "Could not connect... "
        sys.exit(0)
    
    rdb = redis.Redis(host="localhost", port=6379)
    
    def txt2set(fl):
        out = []
        try:
            for l in open(fl, 'r'):
                out.append(l.strip())
        except:
            open(fl, 'w').close()
            print "Warning: empty file %s is created " % fl
            print "Please add your keywords to my_words.txt in one column"
        return set(out)

    hashes = rdb.smembers("bbcnews")
    my_words = txt2set("my_words.txt") # list of keywords in one column
 
    report = ""
    full_report = time.asctime() + "\n\n"
    root = ET.fromstring(data)

    items = root[0].getchildren()
    for item in items:
        item_children = item.getchildren()
        for item_child in item_children:
            if (item_child.tag == "description"):
                if item_child.text:
                    s = item_child.text.replace(",", "").replace(".", "").replace(":", "").replace("'s", "").replace("'", "").replace("-", " ").split()
                    s1 = set(s)
                else:
                    return
                if (my_words & s1):
                    #print "%s - %s" % (item_child.tag, item_child.text)
                    m = hashlib.md5()
                    m.update(item_child.text.encode("utf-8"))
                    h = m.hexdigest()
                    if (not (h in hashes) ):
                        report += item_child.text + "\n\n"
                    full_report += item_child.text + "\n\n"
                    rdb.sadd("bbcnews", h)

    if (report):
        print time.asctime()
        print unicode(report, "utf-8").encode("utf-8") # '\xa3' -> £

    if (parameter == "new"):
        out = report
    else:
        out = full_report

    return out.encode("utf-8")

bbc_rss("all")

