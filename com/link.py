# -*- coding: utf-8 -*-
import datetime
import shutil
import yaml
import hashlib
import urllib2
import re
from StringIO import StringIO
import gzip

def link_stat(ymlfile):

    links = yaml.load(open(ymlfile))
    tags = set()
    tag_list = u""
    for key, val in links.iteritems():
        tags.add(val["tag"])
    for item in tags:
        if isinstance(item, str):
            item = unicode(item, "utf-8")
        tag_list = tag_list + " " + item
    return u"%s records with %s tags" % (len(links.keys()), tag_list)

def link_del(ymlfile, link_id):
    links = yaml.load(open(ymlfile))
    return links.pop(link_id, "None")

def link_uniq(ymlfile, link_id):
    links = yaml.load(open(ymlfile))
    hashes = links.keys()
    if link_id in hashes:
        return False
    return True
    
def link_tag(ymlfile, tag):
    links = yaml.load(open(ymlfile))
    count = 0
    report = ""
    for key, val in links.iteritems():
        if val["tag"] == tag:
            report += val["link"] + " - " + val["title"] + "\n"
            count += 1
    return u"%s--\nFound: %s records with tag %s" % (report, count, tag)

def link_url(ymlfile, url):
    links = yaml.load(open(ymlfile))
    count = 0
    report = ""
    for key, val in links.iteritems():
        if url in val["link"]:
            report += val["link"] + " - " + val["title"] + "\n"
            count += 1
    return u"%s--\nFound: %s records with url %s" % (report, count, url)

def link_title(ymlfile, title):
    """
    Search pattern in title record
    Ignore case for cyrillic - hack with lower case
    """
    links = yaml.load(open(ymlfile))
    count = 0
    report = ""
    ptitle = re.compile( title.lower(), re.L | re.I) # re.I not work with cyrillic?
    for key, val in links.iteritems():
        if isinstance(val["title"], str):
            uttl = unicode(val["title"], "utf-8").lower() # hack
        else:
            uttl = val["title"].lower()
        if ptitle.search( uttl  ):
            report += val["link"] + " - " + val["title"] + "\n"
            count += 1
    return u"%s--\nFound: %s records with title %s" % (report, count, title)

def link_search(ymlfile, keyword):
    report = u""
    report += link_url(ymlfile, keyword) + "\n"
    report += link_tag(ymlfile, keyword) + "\n"
    report += link_title(ymlfile, keyword) + "\n"
    return report

def link_add(ymlfile, link, tag):
    """
    GET page from link
    Parse charset, title
    Save data to yml file
    """
    elink = link.encode("idna")
    if "http" not in link:
        lnk = "https://" + link
        try:
            res = urllib2.urlopen("https://" + elink, None, 3)
        except:
            lnk = "http://" + elink
            try:
                res = urllib2.urlopen("http://" + elink, None, 3)
            except:
                return "Error url"
    else:
        lnk = link
        sep = r"://"
        prefix, elink = link.split(sep)
        elink = elink.encode("idna")
        try:
            res = urllib2.urlopen(prefix + sep + elink, None, 3)
        except:
            return "Error url"

    if res.info().get('Content-Encoding') == 'gzip':
        buf = StringIO( res.read())
        ff = gzip.GzipFile(fileobj=buf)
        data = ff.read()
    else:   
        data = res.read()
    charset = res.info().getparam("charset")

    pattern = re.compile("<title>(.*?)</title>", re.I)
    title1 = pattern.findall(data)
    if title1:
        title = pattern.findall(data)[0]
        utitle = unicode(title, charset)
    else:
        utitle  = ""

#    print "utitle: ", utitle
    
    today = datetime.date.today()
    m = hashlib.md5()
    m.update(lnk.encode("utf-8"))
    link_id = (m.hexdigest())[-8:]

    if not link_uniq(ymlfile, link_id):
        return "Error: duplicate link..."

    shutil.copy2(ymlfile, ymlfile + "~")

    record = u'''%s:
    link: "%s"
    title: "%s"
    tag: "%s"
    date: "%s"
''' % (link_id, lnk, utitle, tag, today)
    
#    print record
    
    with open(ymlfile, "a") as f:
        f.write(record.encode("utf-8")) # we will use exactly utf-8

    return u"%s \t %s \n %s" % (lnk.lower(), utitle, link_stat(ymlfile))


def link_cmd(cmd):
    '''
    link <cmd> <options>
      cmd:  
        "add <url> <tag>" - adding new record
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
        return link_tag(ymlfile, c[1].lower())
    elif c[0] == "url":
        if len(c) != 2:
            return "Error"
        return link_url(ymlfile, c[1].lower())
    elif c[0] == "title":
        if len(c) != 2:
            return "Error"
        return link_title(ymlfile, c[1])
    elif c[0] == "search":
        if len(c) != 2:
            return "Error"
        return link_search(ymlfile, c[1])
    elif c[0] == "add":
        if len(c) != 3:
            return "Usage: link add <url> <tag>"
        return link_add(ymlfile, c[1], c[2].lower())
    else:
        return "None"

#print link_cmd("")
