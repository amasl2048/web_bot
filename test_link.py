# -*- coding: utf-8 -*-
from com.link import link_cmd

with open("links.csv", "r") as f:
    for line in f.readlines():
        url, tag = line.split(";", 2)
        cmd = u"add " + \
        unicode(url.strip(), "utf-8") + " " + \
        unicode(tag.strip(), "utf-8")
        print cmd
        print link_cmd(cmd)

