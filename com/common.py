import yaml
import os.path
import time

config = yaml.load(open("/etc/bot.config"))
log_file = os.path.join(config["work_dir"], config["log_file"])

def prnt_log(msg):
    with open(log_file, "a") as f:
        f.write("[%s] %s\n" % (time.strftime("%c"), msg))
