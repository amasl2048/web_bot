#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import pyelliptic
import base64
import shutil, datetime

def memo_save(myfile, key, data):
    iv = pyelliptic.Cipher.gen_IV('bf-cfb')
    bi = base64.encodestring(iv)
    ctx = pyelliptic.Cipher(key, iv, 1, ciphername='bf-cfb')

    ciphertext = ctx.update(data.encode("utf-8"))
    ciphertext += ctx.final()
    ctext = base64.encodestring(ciphertext)

    shutil.copy2(myfile, myfile + "~")
    shutil.copy2(myfile + ".iv", myfile + ".iv~")
    with open(myfile, "w") as f:
        f.write(ctext) 
    with open(myfile + ".iv", "w") as f:
        f.write(bi)
    return

def memo_add(myfile, note, key, data):
    """
    Add data to yml file
    """
    today = datetime.date.today()
    note_id = base64.b32encode(str(os.urandom(3))).strip()[:5] # first 5 chars

    record = u'''%s:
    date: %s
    note: %s
''' % (note_id, today, note)
    data += record
    memo_save(myfile, key, data)
    return 

def memo_clear(myfile, key):
    """
    Add data to yml file
    """
    memo_save(myfile, key, "---\n")
    return

