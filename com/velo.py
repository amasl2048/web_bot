from pandas import read_csv
from numpy import timedelta64
import time, datetime
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

t_year = int(time.strftime("%Y")) # this year

if debug:
    print "velo work: ", work

def str2time(Series):
    patt = re.compile("(\d+):(\d+)")
    h,m = patt.search(Series).groups()
    return datetime.timedelta(hours=int(h), minutes=int(m))

def time2hours(Series):
    return Series

def velo_stat(csvfile, year):
    df_all = read_csv(csvfile, sep='\t', header=0, index_col=0, parse_dates=[1])
    #st_all = df_all["date"].size
    today = datetime.datetime.today()
    # filter only this year
    df = df_all[ (df_all["date"] > datetime.datetime(year, 1, 1)) & (df_all["date"] < datetime.datetime(year+1, 1, 1)) ]
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

def velo_top(csvfile):
    df_all = read_csv(csvfile, sep='\t', header=0, index_col=0, parse_dates=[1])
    # more distance
    report = str(df_all.sort(["km"], ascending=False)[:3][["date", "km"]])

    # longest time
    df_all["timedelta"] = df_all["time"].map(str2time)
    report += "\n" + str( df_all.sort(["timedelta"], ascending=False)[:3][["date", 'time']])

    # fastest speed
    df_all["hours"] = df_all.timedelta / timedelta64(1, "h")
    df_all["speed"] = df_all.km / df_all.hours 
    report += "\n" + str(df_all.sort(["speed"], ascending=False)[:3][["date", "time", "km", "speed"]])
    
    return report
    
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

    return velo_stat(csvfile, t_year)

def velo_cmd(cmd):
    '''
    velo <cmd> <options>
      cmd:  
        "add <h:mm> <km>"  - adding new data to csv
        "help" - print help
        "stat [year]" - return velo statistics for the year
        "work" - add default time/distance to work
        "top" - the best achievement
    '''
    if debug:
        print "velo", cmd

    if cmd == "":
        cmd = "stat" 
    c = cmd.split()
    if c[0] == "stat":
        if len(c) == 2:
            return velo_stat(csvfile, int(c[1]))
        return velo_stat(csvfile, t_year)
    elif c[0] == "help":
        return velo_cmd.__doc__
    elif c[0] == "top":
        return velo_top(csvfile)
    elif c[0] == "work":
        return velo_add(csvfile, work[0], work[1])
    elif c[0] == "add":
        if len(c) != 3:
            return "Error"
        return velo_add(csvfile, c[1], c[2])

#print velo_cmd("top")
