from machine import Pin
from machine import Timer
import os
import urequests
import ntptime
import dht
import network
import socket
import time
import ujson
import GETBH1750
import gc
gc.collect()

WAIT_FOR_CONNECT=10
syspam={}
sysgpio={}
tim = Timer(-1)
tmoffsetdat=0
rhoffsetdat=0
chksw = Pin(16, Pin.IN)#D0
#d = dht.DHT22(Pin(0))#D3
#d = GETBH1750.getds18x20()#D3
#lux = GETBH1750.getlux()
wifiled = Pin(2, Pin.OUT)#D4
R1 = Pin(12, Pin.OUT)#D6
R2 = Pin(13, Pin.OUT)#D7
R3 = Pin(14, Pin.OUT)#D5
R4 = Pin(15, Pin.OUT)#D8
tick_count=1
wifi_count=0
wifiled_flag=0
inchksw=1
R1 = Pin(12, Pin.OUT)#D6
R2 = Pin(13, Pin.OUT)#D7
R3 = Pin(14, Pin.OUT)#D5
R4 = Pin(15, Pin.OUT)#D8

errhtml="""
<!DOCTYPE html><html><head><title>err set</title></head><body>ERR Clinet!</body></html>
"""
setaphtml="""
<!DOCTYPE html><html><head><title>AP Setup</title></head><body>%s</body></html>
"""
form="""
<form method=get action='/update_ap'><table border="0">
<tr><td>SSID</td><td><input name=ssid type=text value=%s></td></tr>
<tr><td>PWD </td><td><input name=pwd type=text></td></tr>
<tr><td></td><td align=right><input type=submit value=Connect></td></tr>
</table></form>
<form method="get" action="/update_url"><table border="0">
<tbody><tr><td>SENDURL:</td><td><input name="UPLOADURL" type="text" value=%s></td></tr>
<tr><td>KEYID: </td><td><input name="LINKID" type="text" value=%s></td></tr>
<tr><td>UPTIME(30): </td><td><input name="UPLOADTIME" type="text"  value=%s></td></tr>
<tr><td></td><td align="right"><input type="submit" value="SETUP"></td></tr>
</tbody></table></form>
"""
passform="""
 <html><head></head><body><form method="get" action="/SETGPIO?"><table border="0">
 <tbody><tr><td>Link PASS</td></tr><tr><td>IP=%s</td></tr></tbody></table></form></body></html>
"""
gpiohtml="""<!DOCTYPE html><html><head><title>ESP8266 Pins</title></head>
<body><h1>ESP8266 Pins</h1><table border="1"><tr><th>Pin</th><th>Value</th><th>Action</th></tr>%s</table>
</body></html>
"""

def loadjpam(jfilename):
    file = open(jfilename,"r")
    jobj = ujson.loads(file.read())
    file.close()
    return jobj
def writejpam(jfilename,jobj):
    wfile = open(jfilename,"w")
    wfile.write(ujson.dumps(jobj))
    wfile.close()
def chkurl(ss):
    ss2=""
    i=0
    while i < len(ss):
        if ss[i]=='%':
            cc=ss[i+1]+ss[i+2]
            ss2=ss2+chr(int(cc,16))
            i=i+3
        else:
            ss2=ss2+ss[i]
            i=i+1    
    return ss2
if __name__ == '__main__':
    pass



