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
        "del <url>"
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
        dat = urllib.urlencode({"del": c[1].encode("utf-8")})
        return get_link(dat)

    elif c[0] == "tag":
        if len(c) != 2:
            return "Error"
        dat = urllib.urlencode({"tag": c[1].encode("utf-8")})
        return get_link(dat)

    elif c[0] == "url":
        if len(c) != 2:
            return "Error"
        dat = urllib.urlencode({"url": c[1].encode("utf-8")})
        return get_link(dat)

    elif c[0] == "title":
        if len(c) != 2:
            return "Error"
        dat = urllib.urlencode({"title": c[1].encode("utf-8")})
        return get_link(dat)

    elif c[0] == "search" or c[0] == "s":
        if len(c) != 2:
            return "Error"
        dat = urllib.urlencode({"search": c[1].encode("utf-8")})
        return get_link(dat)

    elif c[0] == "add":
        if len(c) < 3:
            return "Usage: link add <url> <tag>"
        dat = urllib.urlencode({"add": cmd[4:].encode("utf-8")})
        return get_link(dat)

    else:
        return "None"

#print link_cmd("")
