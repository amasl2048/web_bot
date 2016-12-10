import math

def fspl(cmd):
    '''
    Rerutn Free-space path loss (FSPL) in dB
    fspl <Mhz> <meters>
    '''
    if cmd == "":
        return fspl.__doc__
    
    c = cmd.split()
    #f = 2400 # MHz
    #d = 10 # m
    
    if len(c) != 2:
        return fspl.__doc__
    
    try:
        f = float(c[0])
        d = float(c[1])
    except:
        return "Type error"
    
    if not ((f > 0) and f < (1000 * 1000)):
        return "f Range Error"
    if not ((d > 0) and d < (1000 * 1000)):
        return "d Range Error"
    
    const = -27.55 # for meters and MHz
    fspl = 20 * math.log10(d) + 20 * math.log10(f) + const
    
    return "%.1f dB" % fspl

#print fspl("2400 10")
