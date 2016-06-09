import redis
import requests
import hashlib
import yaml
import os
import re
'''
Checking does web content changed

'''

def content_cmd():

    config = yaml.load(open("/etc/bot.config"))
    log_file = os.path.join(config["work_dir"], config["log_file"])

    def prnt_log(msg):
        with open(log_file, "a") as f:
            f.write(msg + "\n")

    rdb = redis.Redis(host="localhost", port=6379)

    url = config["content"]["url"]

    body_patt  = re.compile(r"<body.*</body>", re.S)
    hdr_patt   = re.compile(r"<header.*</header>", re.S)
    sesid = re.compile(';jsessionid=(.*?)\" >', re.S)

    req = requests.get(url)

    if req.ok:
        m = hashlib.md5()
        b1 = body_patt.findall(req.content)[0] # find body
        hdr = hdr_patt.findall(b1)[0] # find header
        b2 = b1.replace(hdr, "") # remove header
        js = sesid.findall(b2)[1] # the second item is correctly match
        body = b2.replace(js, "") # remove id
        m.update(body)
        h = m.hexdigest()
        with open("body.htm", "w") as f:
            f.writelines(body)
        last = rdb.get("cont")
        if h == last:
            prnt_log("Content not changed.")
        else:
            prnt_log("New: %s, last: %s" % (h, last) )
            rdb.set("cont", h)
            return "Content: %s has changed" % url
    else:
        prnt_log(req.status_code)

#print content_cmd()