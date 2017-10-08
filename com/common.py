'''
Common part
'''
import os
import time
import yaml

config = yaml.load(open(os.environ["BOT_CFG"]))  #"/etc/bot.config"))
log_file = os.path.join(config["work_dir"], config["log_file"])

def prnt_log(msg):
    '''Loging function'''
    with open(log_file, "a", encoding='utf8') as f:
        f.write("[%s] %s\n" % (time.strftime("%c"), msg))
