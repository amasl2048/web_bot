#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import re
import subprocess
import yaml

import common
'''
Traffic stats in Mbytes
per week/month
'''

def traffic_report(param):
    '''
    param:
      today  - only traff data from last update
      update - rewrite traff yml file
    '''
    interface = common.config["traff"]["iface"]

    rx = re.compile(r"RX bytes:([0-9]+) \(", re.S)
    tx = re.compile(r"TX bytes:([0-9]+) \(", re.S)

    template = '''%s:
    rx: %s
    tx: %s
    week_in: %s
    week_out: %s
    month_in: %s
    month_out: %s
    tm: %s
    '''

    traf_dat = common.config["traff"]["dat_file"]
    tm = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())
    week = time.strftime("%w")
    day  = time.strftime("%d")
    try:
        traf_stat = yaml.load(open(traf_dat))
    except:
        stat = template % (interface[0], 0, 0,
                           0, 0, 0, 0,
                           tm)
        #print report
        dat = open(traf_dat, "w")
        dat.writelines(stat)
        dat.close()
        traf_stat = yaml.load(open(traf_dat))

    last_receive = traf_stat[interface[0]]["rx"]
    last_send   = traf_stat[interface[0]]["tx"]

    common.prnt_log("Starting...")#, time.strftime("%A, %d. %B %Y %H:%M")

    output = subprocess.Popen(["/sbin/ifconfig", interface[0]], shell=True, stdout=subprocess.PIPE).communicate()[0]
    uptime = subprocess.Popen(["/usr/bin/uptime", "-p"],        shell=True, stdout=subprocess.PIPE).communicate()[0]

    receive = int( rx.findall(output)[0] ) # bytes from ifconfig
    send    = int( tx.findall(output)[0] )

    if (receive > last_receive):
        rx_diff = receive - last_receive
    else:
        rx_diff = receive

    if (send > last_send):   
        tx_diff = send - last_send
    else:
        tx_diff = send

    # counters weekly / monthly
    rx_week  = traf_stat[interface[0]]["week_in"]   + rx_diff 
    tx_week  = traf_stat[interface[0]]["week_out"]  + tx_diff
    rx_month = traf_stat[interface[0]]["month_in"]  + rx_diff
    tx_month = traf_stat[interface[0]]["month_out"] + tx_diff 

    def mb(b):
        return round( (b /1000. / 1000.) , 1 )
    
    out = '''%s\t receive/send Mb
Daily:\t %s/%s
Weekly:\t %s/%s
Monthly:\t %s/%s
Eth:\t %s/%s
uptime: %s''' % (interface[0],
		mb(rx_diff),  mb(tx_diff),
                mb(rx_week),  mb(tx_week),
                mb(rx_month), mb(tx_month),
                mb(receive),  mb(send),
                uptime)
    
    common.prnt_log(out)
    # reset counters
    if week == "0":
        rx_week = 0
        tx_week = 0
    if day == "01":
        rx_month = 0
        tx_month = 0
    
    stat = template % (interface[0], receive, send,
                       rx_week,  tx_week,
                       rx_month, tx_month,
                       tm)

    if (param == "update"):
      dat = open(traf_dat, "w")
      dat.writelines(stat)
      dat.close()
    elif (param == "today"):
        return out

    limit = int(common.config["traff"]["limit"])
    if (mb(rx_diff) > limit) or (mb(tx_diff) > limit): # not report less 200Mb
        return out

    return ""
#print traffic_report("update")
