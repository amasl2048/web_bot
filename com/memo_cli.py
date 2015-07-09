# -*- coding: utf-8 -*-
import urllib, urllib2
import re

def get_memo(post):
    localhost = "https://localhost:8880/memo"
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

def memo_cmd(cmd):
    '''
    memo <cmd> <options>
      cmd:  
        add <note> - adding new record
        show - display all notes
        clear - delete all notes
        help - print help
        stat - return statistics       
    '''

    if cmd == "":
        cmd = "show" 
    c = cmd.split()
    if c[0] == "help":
        return memo_cmd.__doc__
    elif c[0] == "stat":
        dat = urllib.urlencode({"stat": "all"})
        return get_memo(dat)
    elif c[0] == "show":
        dat = urllib.urlencode({"show": "all"})
        return get_memo(dat)
    elif c[0] == "clear":
        dat = urllib.urlencode({"clear": "all"})
        return get_memo(dat)
    elif c[0] == "add":
        dat = urllib.urlencode({"add": cmd[4:].encode("utf-8")})
        return get_memo(dat)
    else:
        return "None"

# print memo_cmd("clear")
# print memo_cmd("add ещё тест")
# print memo_cmd("show")
