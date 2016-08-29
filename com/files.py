import yaml
import os, time
import redis
'''
Check files changes if not zero size
'''

def files_cmd():

    # read config
    config = yaml.load(open("/etc/bot.config"))
    log_file = os.path.join(config["work_dir"], config["log_file"])

    files_list = config["files"]["list"]

    def prnt_log(msg):
        with open(log_file, "a") as f:
            f.write("[%s] %s\n" % (time.strftime("%c"), msg))

    def zero_file(fl):
        sz = os.path.getsize(fl)
        if sz == 0:
            return True
        else:
            return False

    def stat_file(fl):
        stat = os.stat(fl)
        fl_stat = dict(size = stat.st_size,
                       time = stat.st_mtime)
        return fl_stat

    report = ""
    for afile in files_list:
        if os.path.exists(afile):
            if not zero_file(afile):
                st = stat_file(afile)
                report += '''%s is changed
  time: %s
  size: %s bytes''' % (os.path.basename(afile),
                 time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st["time"])),
                 st["size"])
        else:
            prnt_log("%s not exists" % afile)
    return report

#print files_cmd()
