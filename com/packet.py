#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Calculate packet transmission time from given packet size and link rate
'''

import math

def vmulty(let):
    if let == "b":
        multy = 1
    elif let == "k":
        multy = 1024
    elif let == "K":
        multy = 1000
    elif let == "m":
        multy = 1024 * 1024
    elif let == "M":
        multy = 1000 * 1000
    elif let == "g":
        multy = 1024 * 1024 * 1024
    elif let == "G":
        multy = 1000 * 1000 * 1000
    elif let == "t":
        multy = 1024 * 1024 * 1024 * 1024
    elif let == "T":
        multy = 1000 * 1000 * 1000 * 1000
    elif let == "p":
        multy = 1024 * 1024 * 1024 * 1024 * 1024
    elif let == "P":
        multy = 1000 * 1000 * 1000 * 1000 * 1000
    
    return multy

def lmulty(ti):

    til = math.log10(ti)
    #print til
    if til >= 0:
        nm = "s"
        new_ti = ti
    elif til < 0 and til > -3:
        nm = "ms"
        new_ti = ti * 1000
    elif til <= -3 and til > -6:
        nm = "us"
        new_ti = ti * 1000 * 1000
    elif til <= -6 and til > -9:
        nm = "ns"
        new_ti = ti * 1000 * 1000 * 1000
        
    return new_ti, nm


def pkts(sz, rate):
    '''
    sz: packet size - b, k, m, g, t, p (multiply by 1024)
    rate: link rate - K, M, G, T (multiply by 1000)
    1500b 100M

    return: 120 us
    '''

    l_sz   = len(sz)
    l_rate = len(rate)
    
    sz_v   = sz[l_sz - 1: l_sz]
    rate_v = rate[l_rate -1: l_rate]

    p_sz = float(sz[0: l_sz -1])
    p_rate = float(rate[0: l_rate -1])
    
    sz_m   = vmulty(sz_v)
    rate_m = vmulty(rate_v)
    #print p_sz, sz_v, p_rate, rate_v

    # 8 bits per byte
    ti = (p_sz * sz_m * 8) / (p_rate * rate_m)

    out_ti, out_v = lmulty(ti)
    return out_ti, out_v

def pkts_cmd(cmd):
    ''' Usage: packet <size> <rate>
    size: packet size (bytes) - b, k, m, g, t, p (multiply by 1024)
    rate: link rate (bits per sec) - K, M, G, T (multiply by 1000)

    >packet 1500b 100M
    '''
    if cmd == "":
        return pkts_cmd.__doc__ 
    c = cmd.split()

    if len(c) != 2:
        return pkts_cmd.__doc__ 
    
    sz   = c[0]
    rate = c[1]

    return "%s %s" % pkts(sz, rate)
    
#print pkts_cmd("1500b 100M")
