from pandas import read_csv
import time, datetime

def velo_stat():
    df = read_csv('velo.csv', sep='\t', header=0, index_col=0, parse_dates=[1,2])
    #f = lambda x: round(x, 2)
    #print df
    #stoday = time.strftime("%Y-%m-%d")
    today = datetime.datetime.today()
    s = df["date"].size

    out = """Totaly:\t%s km %s times
Avg:\t%s km per day
Last:\t%s days
Velo:\teach %s days
"""  % (df["km"].sum(), s,
    round(df["km"].sum() / s, 1),
    (today - df["date"][s]).days,
    (today - df["date"][1]).days / s 
    )

    return out

#print velo_stat()
