#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import re
import subprocess
import yaml
'''
Traffic stats in Mbytes
per week/month
'''

def traffic_report():
    interface = ["eth0"]

    rx = re.compile(r"RX bytes:([0-9]+) \(", re.S)
    tx = re.compile(r"TX bytes:([0-9]+) \(", re.S)

    template = '''%s:
        rx: %s
        tx: %s
        tm: %s
    '''

    traff = "traf_report.yml"
    tm = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())
    try:
        traf_stat = yaml.load(open(traff))
    except:
        stat = template % (interface[0], 0, 0, tm)
        #print report
        dat = open(traff, "w")
        dat.writelines(stat)
        dat.close()
        traf_stat = yaml.load(open(traff))

    last_recive = traf_stat[interface[0]]["rx"]
    last_send   = traf_stat[interface[0]]["tx"]

    print "\nStarting... \n--- ", time.strftime("%A, %d. %B %Y %H:%M")

    output = subprocess.Popen(["ifconfig", interface[0]], stdout=subprocess.PIPE).communicate()[0]
    uptime = subprocess.Popen(["uptime", "-p"],           stdout=subprocess.PIPE).communicate()[0]

    recieve = round( int( rx.findall(output)[0] )/1000./1000. , 2) # Mbytes
    send    = round( int( tx.findall(output)[0] )/1000./1000. , 2)

    out = "Send: %s Mb\nRecieve: %s Mb\nuptime: %s" % (recieve - last_recive, send - last_send, uptime)

    stat = template % (interface[0], recieve, send, tm)
    #print report
    dat = open(traff, "w")
    dat.writelines(stat)
    dat.close()
    return out

#print traffic_report()
