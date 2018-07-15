import time
import datetime
import re
import shutil
import pandas as pd
from numpy import timedelta64

import common
'''
Module
-----
Save recived tracking data to csv file:
velo_cmd("add <hh:mm> <km>")

Printing data statistics:
velo_cmd("velo stat")
'''

# read config

DEBUG = common.config["velo"]["debug"]
CSV = common.config["velo"]["csvfile"]
WORK = common.config["velo"]["work"]

t_year = int(time.strftime("%Y")) # this year

if DEBUG:
    common.prnt_log("velo work: %s" % WORK)

def str2time(Series):
    patt = re.compile("(\d+):(\d+)")
    h,m = patt.search(Series).groups()
    return datetime.timedelta(hours=int(h), minutes=int(m))

def td2min(tdelta):
    '''Convert timedelta to hh mm
    for python 2.7.12
    '''
    tts = tdelta.total_seconds()
    hours = int(tts/60./60.)
    minutes = int((tts - hours * 3600)/60.)
    return "%sh %sm" % (hours, minutes)

def dec2min(hours):
    ''' For python 2.7.6 '''
    h = int(hours)
    m = hours - h
    return "%sh %sm" % (h, int(60 * m) )

def velo_stat(csvfile, year):
    df_all = pd.read_csv(csvfile, sep='\t', header=0, index_col=0, parse_dates=[1])
    #st_all = df_all["date"].size
    today = datetime.datetime.today()
    # filter only this year
    df = df_all[ (df_all["date"] > datetime.datetime(year, 1, 1)) & (df_all["date"] < datetime.datetime(year+1, 1, 1)) ]
    st = df["date"].size
    if st == 0:
        return "Null"
    df.loc[:,("timedelta")] = df["time"].map(str2time)
    ttime = df["timedelta"].sum()  # for python 2.7.12
    #ttime = df["timedelta"].sum()/1000/1000/1000/60/60.  # hack for python 2.7.6
    '''
    In old python 2.7.6 the dtype of 'timedelta' is numpy.int64 instead of timedelta.
    In python 2.7.12 timedelta.sum() returns timedelta
    '''

    out = """Totaly:\t%.1f km %s times
Time:\t%s
Avg:\t%s km per day
Last:\t%s days
Velo:\teach %s days
"""  % (df["km"].sum(), st,
    td2min(ttime),    # for python 2.7.12
    #dec2min(ttime),  # for python 2.7.6
    round(df["km"].mean(), 1),
    (today - df.loc[df.index.tolist()[-1], "date"]).days, # last item
    (today - df.loc[df.index.tolist()[0], "date"]).days / st # first item
    )

    return out

def velo_top(csvfile):
    df_all = pd.read_csv(csvfile, sep='\t', header=0, index_col=0, parse_dates=[1])
    # more distance
    report = str(df_all.sort_values(by="km", ascending=False)[:3][["date", "km"]])

    # longest time
    df_all["timedelta"] = df_all["time"].map(str2time)
    report += "\n" + str( df_all.sort_values(by="timedelta", ascending=False)[:3][["date", 'time']])

    # fastest speed
    df_all["hours"] = df_all.timedelta / timedelta64(1, "h")
    df_all["speed"] = df_all.km / df_all.hours 
    report += "\n" + str(df_all.sort_values(by="speed", ascending=False)[:3][["date", "time", "km", "speed"]])
    
    return report

def velo_last(csvfile):
    df_all = pd.read_csv(csvfile, sep='\t', header=0, index_col=0, parse_dates=[1])
    ids = df_all.sort_values(by="date").index.tolist()[-1]
    report = str(df_all.loc[ids])

    # longest time
    df_all["timedelta"] = df_all["time"].map(str2time)
    ltime = df_all.sort_values(by="timedelta", ascending=False)
    for i, elem in enumerate(ltime.index.tolist()):
        if elem == ids:
            report += "\nRate:\n %s for time" % str(i+1)
    
    # distance
    distance = df_all.sort_values(by="km", ascending=False)
    for i, elem in enumerate(distance.index.tolist()):
        if elem == ids:
            report += "\n %s for distance" % str(i+1)
    
    # speed
    df_all["hours"] = df_all.timedelta / timedelta64(1, "h")
    df_all["speed"] = df_all.km / df_all.hours 
    speed = df_all.sort_values(by="speed", ascending=False)
    for i, elem in enumerate(speed.index.tolist()):
        if elem == ids:
            report += "\n %s for speed %s" % (str(i+1), str(round(df_all["speed"].loc[ids],1)))

    return report
    
def velo_add(csvfile, today, t, km):

    ptime = re.compile("^\d{1,2}:\d{2}$")
    if not ptime.search(t):
        return "Error time"
    
    pkm = re.compile("^\d+\.?\d{0,2}$")
    if not pkm.search(km):
        return "Error km"

    df = pd.read_csv(csvfile, sep='\t', header=0, index_col=0, parse_dates=[1,2])
    #today = datetime.date.today()
    s = df["date"].size

    shutil.copy2(csvfile, csvfile + "~")
    row = "%s\t%s\t%s\t%s\n" % (s+1, today, t, km)
    with open(csvfile, "a") as f:
        f.write(row)

    return velo_last(csvfile)

def velo_cmd(cmd):
    '''
    velo <cmd> <options>
      cmd:  
        "add <h:mm> <km>"  - adding new data to csv
        "date <yyyy-mm-dd> <h:mm> <km>" - adding new data for the date
        "help" - print help
        "stat [year]" - return velo statistics for the year
        "work" - add default time/distance to work
        "top" - the best achievement
        "last" - last item
    '''
    if DEBUG:
        common.prnt_log("velo %s" % cmd)

    if cmd == "":
        cmd = "stat"
    c = cmd.split()

    if c[0] == "stat":
        if len(c) == 2:
            return velo_stat(CSV, int(c[1]))
        return velo_stat(CSV, t_year)
    elif c[0] == "help":
        return velo_cmd.__doc__
    elif c[0] == "top":
        return velo_top(CSV)
    elif c[0] == "last":
        return velo_last(CSV)

    elif c[0] == "work":
        tod = datetime.date.today()
        return velo_add(CSV, str(tod), WORK[0], WORK[1])

    elif c[0] == "add":
        if len(c) != 3:
            return "Error add"
        tod = datetime.date.today()
        return velo_add(CSV, str(tod), c[1], c[2])

    elif c[0] == "date":
        if len(c) != 4:
            return "Error date args"
        ptd = re.compile("^\d{4}-\d{2}-\d{2}$")
        if not ptd.search(c[1]):
            return "Error date"
        return velo_add(CSV, c[1], c[2], c[3])

'''
print velo_cmd("last")
print velo_cmd("stat")
print velo_cmd("top")
'''
