#!/usr/bin/env python
# -*- coding: utf-8 -*-
import redis
import json
import hashlib
import base64
import datetime

import common

def notify_once(dt, content):
    '''
    Store event with date and content
        dt: <YYYY-MM-DD> 
        content: <text>
    '''
    
    jdata = {"type":    "once",
             "date":    dt,
             "content": content}

    jdump = json.dumps(jdata)      #; print jdump

    mh = hashlib.md5()
    mh.update(jdump)
    hinfo = mh.hexdigest()         #; print hinfo
    key = base64.b32encode(hinfo)  #; print key  # key is a content hash
    
    rdb = redis.Redis(host="localhost", port=6379)
    rkey = "notify:" + key[:5]  # first 5 chars
    rdb.set(rkey, jdump)

    dtime = datetime.datetime.strptime(dt, "%Y-%m-%d")
    rdb.zadd("notify:index", rkey, dtime.toordinal())  # Gregorian ordinal of the date

    return rkey, jdump

def get_event(td):
    '''
    Get events report for <td> day
       td = 0 today
       td = 1 tomorrow
       td = 7 in a week
    '''

    today = datetime.date.today()
    tday  = today.toordinal()  #; print tday  # Gregorian ordinal of the date

    rdb = redis.Redis(host="localhost", port=6379)
    events = rdb.zrangebyscore("notify:index", tday+td, tday+td)  #; print events

    report = ""
    for event in events:
        item = json.loads( rdb.get(event).decode() ) 
        report = report + "\n" + item["content"]

    when = today + datetime.timedelta(days=td)
        
    return when.strftime("%a, %d %b:"), report      #TODO: utf8 report


def view_event(sdate):
    ''' View event raw data from the given sdate YYYY-MM-DD'''
    
    try:
        dtime = datetime.datetime.strptime(sdate, "%Y-%m-%d")
    except:
        return "Date format: YYYY-MM-DD"

    rdb = redis.Redis(host="localhost", port=6379)

    events = rdb.zrangebyscore("notify:index", dtime.toordinal(), dtime.toordinal())
    report = ""
    for event in events:
        item = json.loads( rdb.get(event).decode() ) 
        report = report + event[-5:] + ":\n" + item["content"] + "\n"

    return report

def del_event(hsh):
    ''' delete event with the hash '''
    
    rdb = redis.Redis(host="localhost", port=6379)
    key = "notify:" + hsh

    try:
        rdb.zrem("notify:index", key)
    except:
        return "Could not get index with: %s" % hsh 
    
    try:
        item = json.loads( rdb.get(key).decode() ) 
    except:
        return "Could not get event with hash: %s" % hsh 

    rdb.delete(key)

    return "Event %s deleted" % item


def event_list(day1, day2):
    
    report = ""
    for i in range(day1, day2):
        when, out = get_event(i)
        if out:
            report += "\n%s %s" % (when, out)
    
    return report


def notify_cmd(cmd):
    ''' 
    notify <cmd> [options]
        cmd:
           "once" <date> <text> - one event at the date
              date: "YYYY-MM-DD"
              text: any content
           "weekly":  "Www" - weekday Mon, Tue, ...     #TODO
           "monthly": "DD"  - day                       #TODO
           "yearly":  "MM-DD" - date                    #TODO
           "each":    "d" - repeat after every "d" day  #TODO

    events <cmd>
       cmd:
           0        - display today events
           1        - tomorrow events
           week     - list from 0 to 6 days
           nextweek - list from 7 to 13 days
           month    - list from 0 to 31 days
           
           view <YYYY-MM-DD>  - view event raw data from the given date
           del <HASH>         - delete event with the hash

    '''
    #common.prnt_log("notify_cmd: %s" % cmd)
    
    if cmd == "":
        cmd = "0"
    c = cmd.split()

    if c[0] == "help":
        return notify_cmd.__doc__

    if c[0] == "once":
        try:
            dtime = datetime.datetime.strptime(c[1], "%Y-%m-%d")
        except:
            return "Date format: YYYY-MM-DD"
        return "%s\n%s" % notify_once(c[1], c[2])

    elif c[0].isdigit():
        return "%s %s" % get_event( int(c[0]) )

    elif c[0] == "week":
        return event_list(0, 6)

    elif c[0] == "nextweek":
        return event_list(6, 13)

    elif c[0] == "month":
        return event_list(0, 31)

    elif c[0] == "view":
        return view_event(c[1])

    elif c[0] == "del":
        return del_event(c[1])
    
    else:
        return "Not implemented"

    return "Empty"
    
#print notify_cmd("month")
