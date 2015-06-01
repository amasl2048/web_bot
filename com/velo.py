from pandas import read_csv
import datetime
import re
import shutil

def velo_stat(csvfile):
    df = read_csv(csvfile, sep='\t', header=0, index_col=0, parse_dates=[1,2])
    today = datetime.datetime.today()
    s = df["date"].size

    out = """Totaly:\t%s km %s times
Avg:\t%s km per day
Last:\t%s days
Velo:\teach %s days
"""  % (df["km"].sum(), s,
    round(df["km"].mean(), 1),
    (today - df.loc[s, "date"]).days,
    (today - df.loc[1, "date"]).days / s 
    )

    return out

def velo_add(csvfile, t, km):
    ptime = re.compile("^\d{1,2}:\d{2}$")
    if not ptime.search(t):
        return "Error"
    pkm = re.compile("^\d+\.?\d{0,2}$")
    if not pkm.search(km):
        return "Error"

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
    '''
    csvfile = "/shared/doc/velo.csv"
    if cmd == "":
        cmd = "stat" 
    c = cmd.split()
    if c[0] == "stat":
        return velo_stat(csvfile)
    elif c[0] == "help":
        return velo_cmd.__doc__
    elif c[0] == "add":
        if len(c) != 3:
            return "Error"
        return velo_add(csvfile, c[1], c[2])
    
#print velo_cmd("")