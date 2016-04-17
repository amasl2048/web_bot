from pandas import read_csv
import datetime
import re
import shutil
import yaml, sys, os
'''
Module
-----
Save recived tracking data to csv file:
velo_cmd("add <hh:mm> <km>")

Printing data statistics:
velo_cmd("velo stat")
'''

# read config
config = yaml.load(open("/etc/bot.config"))
log_file = os.path.join(config["work_dir"], config["log_file"])
sys.stdout = open(log_file, "a")

debug   = config["velo"]["debug"]
csvfile = config["velo"]["csvfile"]
work    = config["velo"]["work"]

if debug:
    print "velo work: ", work

def str2time(Series):
    patt = re.compile("(\d+):(\d+)")
    h,m = patt.search(Series).groups()
    return datetime.timedelta(hours=int(h), minutes=int(m))

def velo_stat(csvfile):
    df_all = read_csv(csvfile, sep='\t', header=0, index_col=0, parse_dates=[1])
    #st_all = df_all["date"].size
    today = datetime.datetime.today()
    t_year = today.year
    # filter only this year
    df = df_all[df_all["date"] > datetime.datetime(t_year, 1, 1)]
    st = df["date"].size
    if st == 0:
        return "Null"
    df["timedelta"] = df["time"].map(str2time)
    ttime = round(df["timedelta"].sum()/1000/1000/1000/60/60., 2)

    out = """Totaly:\t%s km %s times
Time:\t%s hours
Avg:\t%s km per day
Last:\t%s days
Velo:\teach %s days
"""  % (df["km"].sum(), st,
    ttime,
    round(df["km"].mean(), 1),
    (today - df.loc[df.index.tolist()[-1], "date"]).days, # last item
    (today - df.loc[df.index.tolist()[0], "date"]).days / st # first item
    )

    return out

def velo_add(csvfile, t, km):
    ptime = re.compile("^\d{1,2}:\d{2}$")
    if not ptime.search(t):
        return "Error time"
    pkm = re.compile("^\d+\.?\d{0,2}$")
    if not pkm.search(km):
        return "Error km"

    df = read_csv(csvfile, sep='\t', header=0, index_col=0, parse_dates=[1,2])
    today = datetime.date.today()
    s = df["date"].size

    shutil.copy2(csvfile, csvfile + "~")
    row = "%s\t%s\t%s\t%s\n" % (s+1, today, t, km)
    with open(csvfile, "a") as f:
        f.write(row)

    return velo_stat(csvfile)

def velo_cmd(cmd):
    '''
    velo <cmd> <options>
      cmd:  
        "add <h:mm> <km>"  - adding new data to csv
        "help" - print help
        "stat" - return velo statistics
        "work" - add default time/distance to work
    '''
    if debug:
        print "velo: ", cmd

    if cmd == "":
        cmd = "stat" 
    c = cmd.split()
    if c[0] == "stat":
        return velo_stat(csvfile)
    elif c[0] == "help":
        return velo_cmd.__doc__
    elif c[0] == "work":
        return velo_add(csvfile, work[0], work[1])
    elif c[0] == "add":
        if len(c) != 3:
            return "Error"
        return velo_add(csvfile, c[1], c[2])

#print velo_cmd("")
