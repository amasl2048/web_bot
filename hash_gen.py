#! /usr/bin/python
import hashlib
import sys, os, base64
import getpass

try:
    p = sys.argv[1]
except:
    print "Please enter..."
    p = getpass.getpass()
    print "Please enter again..."
    p2 = getpass.getpass()
    if (p != p2):
        print "Error: different passwords"
        sys.exit(1)

salt = base64.encodestring(str(os.urandom(12))).strip()

m = hashlib.sha512()
m.update(p)
m.update(salt)
h = m.hexdigest()

print "\"hash\":", h
print "\"salt\":", salt


