import oath
import base64
import os
import qrcode

secret = base64.encodestring(str(os.urandom(12))).strip()
print secret
key = secret.encode('hex')
print key

b32 = base64.b32encode(secret)
print b32
img = qrcode.make(b32)
img.save("topt.png", "png")

response = oath.totp(key, format='dec6', period=30, hash=hashlib.sha512)
print response

print oath.accept_totp(key, response, format='dec6', period=30, hash=hashlib.sha512)
