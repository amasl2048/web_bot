# -*- coding: utf-8 -*-
import urllib, urllib2
import re

def get_link(post):
    localhost = "https://localhost:8880/link"
    pattern = re.compile("<body>(.*?)</body>", re.I | re.S) 
    try:
      res = urllib2.urlopen(localhost, post)
    except:
      return "No service"
    out = res.read()
    res.close()
    if pattern.findall(out):
        return unicode(pattern.findall(out)[0], "utf=8")
    return "None"

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

    #ymlfile = "./links.yml"
    if cmd == "":
        cmd = "stat" 
    c = cmd.split()
    if c[0] == "help":
        return link_cmd.__doc__

    elif c[0] == "stat":
        dat = urllib.urlencode({"stat": "all"})
        return get_link(dat)

    elif c[0] == "show":
        dat = urllib.urlencode({"show": "all"})
        return get_link(dat)

    elif c[0] == "del":
        if len(c) != 2:
            return "Error"
        dat = urllib.urlencode({"del": cmd[4:].encode("utf-8")})
        #return link_del(ymlfile, c[1])
        return get_link(dat)

    elif c[0] == "tag":
        if len(c) != 2:
            return "Error"
        dat = urllib.urlencode({"tag": cmd[4:].encode("utf-8")})
        #return link_tag(ymlfile, c[1].lower())
        return get_link(dat)

    elif c[0] == "url":
        if len(c) != 2:
            return "Error"
        dat = urllib.urlencode({"url": cmd[4:].encode("utf-8")})
        #return link_url(ymlfile, c[1].lower())
        return get_link(dat)

    elif c[0] == "title":
        if len(c) != 2:
            return "Error"
        dat = urllib.urlencode({"title": cmd[6:].encode("utf-8")})
        #return link_title(ymlfile, c[1])
        return get_link(dat)

    elif c[0] == "search":
        if len(c) != 2:
            return "Error"
        dat = urllib.urlencode({"search": cmd[7:].encode("utf-8")})
        #return link_search(ymlfile, c[1])
        return get_link(dat)

    elif c[0] == "add":
        if len(c) != 3:
            return "Usage: link add <url> <tag>"
        dat = urllib.urlencode({"add": cmd[4:].encode("utf-8")})
        #return link_add(ymlfile, c[1], c[2].lower())
        return get_link(dat)

    else:
        return "None"

#print link_cmd("")
