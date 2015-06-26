# -*- coding: utf-8 -*-
import datetime
import shutil
import yaml
import os, base64
import urllib2
import re

def link_stat(ymlfile):
    links = yaml.load(open(ymlfile))
    tags = set()
    for key, val in links.iteritems():
        tags.add(val["tag"])
    return "%s records with %s tags" % (len(links.keys()), tags)

def link_del(ymlfile, link_id):
    links = yaml.load(open(ymlfile))
    return links.pop(link_id, "None")
    
def link_tag(ymlfile, tag):
    links = yaml.load(open(ymlfile))
    count = 0
    report = ""
    for key, val in links.iteritems():
        if val["tag"] == tag:
            report += val["link"] + " - " + val["title"] + "\n"
            count += 1
    return "%sFound: %s records with tag %s" % (report, count, tag)

def link_url(ymlfile, url):
    links = yaml.load(open(ymlfile))
    count = 0
    report = ""
    for key, val in links.iteritems():
        if url in val["link"]:
            report += val["link"] + " - " + val["title"] + "\n"
            count += 1
    return "%sFound: %s records with url %s" % (report, count, url)

def link_title(ymlfile, title):
    links = yaml.load(open(ymlfile))
    count = 0
    report = ""
    for key, val in links.iteritems():
        if title in val["title"]:
            report += val["link"] + " - " + val["title"] + "\n"
            count += 1
    return "%sFound: %s records with title %s" % (report, count, title)

def link_search(ymlfile, keyword):
    report = ""
    report += link_url(ymlfile, keyword) + "\n"
    report += link_tag(ymlfile, keyword) + "\n"
    report += link_title(ymlfile, keyword) + "\n"
    return report

def link_add(ymlfile, lnk, tag):
    if "http" not in lnk:
        lnk = "http://" + lnk
        #print lnk
    try:
        data = urllib2.urlopen(lnk).read()
        #print data
    except:
        return "Error url"

    patt_charset = re.compile("charset=(.*)\"")
    charset = patt_charset.findall(data)[0]

    pattern = re.compile("<title>(.*)</title>")
    title = pattern.findall(data)[0]
    utitle = unicode(title, charset)
    print charset, title
    print "utitle: ", utitle
    
    today = datetime.date.today()
    link_id = base64.b32encode(str(os.urandom(5))).strip()

    shutil.copy2(ymlfile, ymlfile + "~")

    record = u'''%s:
    link: "%s"
    title: "%s"
    tag: "%s"
    date: "%s"
''' % (link_id, lnk, utitle, tag, today)
    
    print record
    
    with open(ymlfile, "a") as f:
        f.write(record.encode("utf-8"))

    return u"%s \t %s \n %s" % (lnk, utitle, link_stat(ymlfile))


def link_cmd(cmd):
    '''
    link <cmd> <options>
      cmd:  
        "add <link> <tag>" - adding new record
        "del <link_id>"
        "tag <tag>" - find links with tag
        "url <url>" - find links contain url
        "title <title>" - find links contain title
        "search <keyword>" - find links by tag, url and title 
        "help" - print help
        "stat" - return statistics       
    '''
    ymlfile = "./links.yml"
    if cmd == "":
        cmd = "stat" 
    c = cmd.split()
    if c[0] == "stat":
        return link_stat(ymlfile)
    elif c[0] == "help":
        return link_cmd.__doc__
    elif c[0] == "del":
        if len(c) != 2:
            return "Error"
        return link_del(ymlfile, c[1])
    elif c[0] == "tag":
        if len(c) != 2:
            return "Error"
        return link_tag(ymlfile, unicode(c[1],"utf-8"))
    elif c[0] == "url":
        if len(c) != 2:
            return "Error"
        return link_url(ymlfile, unicode(c[1],"utf-8"))
    elif c[0] == "title":
        if len(c) != 2:
            return "Error"
        return link_title(ymlfile, unicode(c[1],"utf-8"))
    elif c[0] == "search":
        if len(c) != 2:
            return "Error"
        return link_search(ymlfile, unicode(c[1],"utf-8"))
    elif c[0] == "add":
        if len(c) != 3:
            return "Error"
        return link_add(ymlfile, unicode(c[1],"utf-8"), c[2])
    else:
        return "None"

print link_cmd("add rbc.ru news")
