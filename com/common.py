'''
Common part
'''
import os
import time
import io
import yaml

config = yaml.load(open(os.environ["BOT_CFG"]))  #"/etc/bot.config"))
log_file = os.path.join(config["work_dir"], config["log_file"])

def prnt_log(msg):
    '''Loging function'''
    with io.open(log_file, "ab", encoding='utf8') as f:
        f.write("[%s] %s\n" % (time.strftime("%c"), msg))
