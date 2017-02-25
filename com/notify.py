#!/usr/bin/env python
# -*- coding: utf-8 -*-
import redis
import json
import hashlib
import base64
import datetime

import common

def notify_me(dt, content):
    '''
    Store event with date and content
        dt: <YYYY-MM-DD> 
        content: <text>
    '''
    
    jdata = {"type":    "ones",
             "date":    dt,
             "content": content}

    jdump = json.dumps(jdata)      #; print jdump

    mh = hashlib.md5()
    mh.update(jdump)
    hinfo = mh.hexdigest()         #; print hinfo
    key = base64.b32encode(hinfo)  #; print key
    
    rdb = redis.Redis(host="localhost", port=6379)
    rkey = "notify:" + key[:5]
    rdb.set(rkey, jdump)

    dtime = datetime.datetime.strptime(dt, "%Y-%m-%d")
    rdb.zadd("notify:index", rkey, dtime.toordinal())

    return rkey, jdump

def get_event(td):
    '''
    Get events report for <td> day
       td = 0 today
       td = 1 tomorrow
       td = 7 in a week
    '''

    today = datetime.date.today()
    tday  = today.toordinal() #; print tday

    rdb = redis.Redis(host="localhost", port=6379)
    events = rdb.zrangebyscore("notify:index", tday+td, tday+td) #; print events

    report = ""
    for event in events:
        item = json.loads( rdb.get(event).decode() ) 
        report = report + "\n" + item["content"]

    when = today + datetime.timedelta(days=td)
        
    return when.isoformat(), report
    
#notify_me("2017-02-27", "test test")
d,r = get_event(2)
print d, r
    
