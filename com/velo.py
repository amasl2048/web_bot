from pandas import read_csv
from numpy import timedelta64
import time, datetime
import re
import shutil
import yaml, os

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

debug   = common.config["velo"]["debug"]
csvfile = common.config["velo"]["csvfile"]
work    = common.config["velo"]["work"]

t_year = int(time.strftime("%Y")) # this year

if debug:
    common.prnt_log("velo work: %s" % work)

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
    df_all = read_csv(csvfile, sep='\t', header=0, index_col=0, parse_dates=[1])
    #st_all = df_all["date"].size
    today = datetime.datetime.today()
    # filter only this year
    df = df_all[ (df_all["date"] > datetime.datetime(year, 1, 1)) & (df_all["date"] < datetime.datetime(year+1, 1, 1)) ]
    st = df["date"].size
    if st == 0:
        return "Null"
    df["timedelta"] = df["time"].map(str2time)
    #ttime = df["timedelta"].sum()
    ttime = df["timedelta"].sum()/1000/1000/1000/60/60. # hack
    '''
    In old python 2.7.6 the dtype of 'timedelta' is numpy.int64 instead of timedelta.
    In python 2.7.12 timedelta.sum() returns timedelta
    '''

    out = """Totaly:\t%s km %s times
Time:\t%s
Avg:\t%s km per day
Last:\t%s days
Velo:\teach %s days
"""  % (df["km"].sum(), st,
    #td2min(ttime),
    dec2min(ttime),
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

def velo_last(csvfile):
    df_all = read_csv(csvfile, sep='\t', header=0, index_col=0, parse_dates=[1])
    id = df_all.sort(["date"]).index.tolist()[-1]
    report = str(df_all.loc[id])

    # longest time
    df_all["timedelta"] = df_all["time"].map(str2time)
    ltime = df_all.sort(["timedelta"], ascending=False)
    for i, elem in enumerate(ltime.index.tolist()):
        if elem == id:
            report += "\nRate:\n %s for time" % str(i+1)
    
    # distance
    distance = df_all.sort(["km"], ascending=False)
    for i, elem in enumerate(distance.index.tolist()):
        if elem == id:
            report += "\n %s for distance" % str(i+1)
    
    # speed
    df_all["hours"] = df_all.timedelta / timedelta64(1, "h")
    df_all["speed"] = df_all.km / df_all.hours 
    speed = df_all.sort(["speed"], ascending=False)
    for i, elem in enumerate(speed.index.tolist()):
        if elem == id:
            report += "\n %s for speed %s" % (str(i+1), str(round(df_all["speed"].loc[id],1)))

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

    return velo_last(csvfile)

def velo_cmd(cmd):
    '''
    velo <cmd> <options>
      cmd:  
        "add <h:mm> <km>"  - adding new data to csv
        "help" - print help
        "stat [year]" - return velo statistics for the year
        "work" - add default time/distance to work
        "top" - the best achievement
        "last" - last item
    '''
    if debug:
        common.prnt_log("velo %s" % cmd)

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
    elif c[0] == "last":
        return velo_last(csvfile)
    elif c[0] == "work":
        return velo_add(csvfile, work[0], work[1])
    elif c[0] == "add":
        if len(c) != 3:
            return "Error"
        return velo_add(csvfile, c[1], c[2])

#print velo_cmd("last")
