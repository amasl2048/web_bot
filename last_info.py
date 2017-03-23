#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from subprocess import Popen,  PIPE

file = "last_reboot.txt"

output = Popen(["uptime", "-s"], stdout=PIPE)
cur_date = str(output.communicate()[0]).strip()

try: 
    f = open(file, "r")
except:
    f = open(file, "w")
    f.write(cur_date)
    f.close()
    sys.exit(0)

last = f.readline().strip()
f.close()

if (cur_date != last):
    report = "last reboot: " + cur_date

    p = Popen(['./xsend.py', report],
        stdout=PIPE,
        stderr=PIPE)
    output, err = p.communicate()
    print output, err
    
    f = open(file, "w")
    f.write(cur_date)
    f.close()

