import oath
import base64
import hashlib

#response = raw_input()

def totp_accept(response):
    if not ( (len(response) == 6) and response.isdigit() ):
        print "Error: wrong response..."
        return False

    try:
        txtfile = open("/etc/totp.txt","r")
        secret = txtfile.readline().strip()
        txtfile.close()
    except:
        print "Error: no totp.txt file..."
        return False

    key = secret.encode('hex')
    del secret

    v,t = oath.accept_totp(key, response, format='dec6', period=30, hash=hashlib.sha512)

    del key
    return v

#print totp_accept(response)
