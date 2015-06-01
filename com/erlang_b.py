#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 Erlang B calculator
 Система с потерями
 Простейший поток требований 
 Показательный закон распределения времени ожидания
 
 inputs: BTH (erlangs), Blocking (refusal probability)
 output: Number of lines

 erlangs limited upto 1M

 Reference calculator:
 http://www.erlang.com/calculator/erlb/
'''
import re

def erlang(cmd):
    '''Usage: erlang <erl> <prob>
    erl  - erlangs
    prob - refusal probability
'''
    limit = 1000*1000 # 1M erlangs
    if cmd == "":
        return erlang.__doc__ 
    c = cmd.split()

    if len(c) != 2:
        return erlang.__doc__ 
    
    erl_p = re.compile("^\d+.?\d?$")
    if not erl_p.search(c[0]):
        return erlang.__doc__ 
    prob_p = re.compile("^[0]\.\d*$")
    if not prob_p.search(c[1]):
        return erlang.__doc__ 
  
    erl  = float(c[0])
    if erl > limit:
      return "erlangs more than 1M"
    prob = float(c[1])
    
    i = 1.0 # blocking probability 1/i
    n = 1

    #print "#lines #blocking"

    while (1/i > prob):
        i = 1 + ( n/erl * i)
        n = n + 1
        #if ( n%100 == 0):
        #    print n, 1/i

    #print "--\nblocking: ", 1/i
    return "%s blocking probability\n%s lines" % (1/i, n-1)

#print erlang("500 0.01")
