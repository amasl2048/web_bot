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

def traffic_report(param):
    '''
    param:
      today  - only traff data from last update
      update - rewrite traff yml file
    '''
    interface = ["eth0"]

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

    traff = "traf_report.yml"
    tm = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())
    week = time.strftime("%w")
    day  = time.strftime("%d")
    try:
        traf_stat = yaml.load(open(traff))
    except:
        stat = template % (interface[0], 0, 0,
                           0, 0, 0, 0,
                           tm)
        #print report
        dat = open(traff, "w")
        dat.writelines(stat)
        dat.close()
        traf_stat = yaml.load(open(traff))

    last_receive = traf_stat[interface[0]]["rx"]
    last_send   = traf_stat[interface[0]]["tx"]

    print "\nStarting... \n--- ", time.strftime("%A, %d. %B %Y %H:%M")

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
    
    out = '''%s     receive/send Mb
Daily:   %s/%s
Weekly:  %s/%s
Monthly: %s/%s
Totaly:  %s/%s
uptime: %s''' % (interface[0],
		mb(rx_diff),  mb(tx_diff),
                mb(rx_week),  mb(tx_week),
                mb(rx_month), mb(tx_month),
                mb(receive),  mb(send),
                uptime)
    print out
    # reset counters
    if week == "0":
        rx_week = 0
        tx_week = 0
    if day == "1":
        rx_month = 0
        tx_month = 0
    
    stat = template % (interface[0], receive, send,
                       rx_week,  tx_week,
                       rx_month, tx_month,
                       tm)

    if (param == "update"):
      dat = open(traff, "w")
      dat.writelines(stat)
      dat.close()
 
    return out

#print traffic_report("update")
