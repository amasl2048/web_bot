import yaml
import os, time

import common
'''
Check files changes if not zero size
'''

def files_cmd():

    # read config
    files_list = common.config["files"]["list"]

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
                out = '''%s is changed
  time: %s
  size: %s bytes''' % (os.path.basename(afile),
                       time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st["time"])),
                       st["size"])
                report += out
                common.prnt_log(out)
            else:
                common.prnt_log("%s is empty" % afile)
        else:
            common.prnt_log("%s not exists" % afile)
    return report

#print files_cmd()
