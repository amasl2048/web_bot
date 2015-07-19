#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, yaml
import pyelliptic
import base64
import shutil, datetime

class Memo:

    def memo_save(self, myfile, key, data):
        '''
        Encrypt and save data to myfile
        '''
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

    def memo_add(self, myfile, note, key, data):
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
        self.memo_save(myfile, key, data)
        return

    def memo_del(self, myfile, id_code, key, data):
        """
        Delete record with given id in yml file
        """
        yaml_data = yaml.load(data)
        if yaml_data.has_key(id_code):
            out = yaml_data.pop(id_code)
        else:
            return ""
        data = yaml.dump(yaml_data, allow_unicode=True, encoding=None, default_flow_style=False) # unicode output
        self.memo_save(myfile, key, data)
        return out["note"]

    def memo_clear(self, myfile, key):
        """
        Clear myfile
        """
        self.memo_save(myfile, key, "---\n")
        return

