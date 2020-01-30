import ntptime
import socket
import time
import ujson
from machine import Pin
from machine import Timer
import webssdset

WAIT_FOR_CONNECT=webssdset.diylib.WAIT_FOR_CONNECT
sta=webssdset.diylib.network.WLAN(webssdset.diylib.network.STA_IF)
sta.active(True)
tim=webssdset.diylib.tim
tmoffsetdat=0
rhoffsetdat=0
chksw = Pin(16, Pin.IN)#D0
#DRVR4=webssdset.diylib.DRVR4#D8
tick_count=webssdset.diylib.tick_count
wifi_count=webssdset.diylib.wifi_count
wifiled_flag=webssdset.diylib.wifiled_flag
inchksw=webssdset.diylib.inchksw
wifiled=webssdset.diylib.wifiled
#SYSPAM=webssdset.diylib.syspam
#SYSGPIO=webssdset.diylib.sysgpio
loadjpam =webssdset.diylib.loadjpam
writejpam=webssdset.diylib.writejpam
def tick(t):
    global tick_count
    global wifiled_flag
    global wifiled
    if tick_count<7200:
        tick_count = tick_count+1
    else:
        tick_count=0
    if "UPLOADTIME" in webssdset.diylib.syspam:
        if webssdset.diylib.syspam["UPLOADTIME"]<=0:
            webssdset.diylib.syspam["UPLOADTIME"]=60
        xx=int(webssdset.diylib.syspam["UPLOADTIME"])*2
    else:
        xx=60
        webssdset.diylib.syspam=loadjpam("JSYSPAM.json")
        print("reload jsysoam files ...")
    if (tick_count%xx)==0:
        webssdset.diylib.syspam["GETTIME"]=now()
        webssdset.diylib.sysgpio["F1"]["DAT"],webssdset.diylib.sysgpio["F2"]["DAT"] =  getdht22()
        if webssdset.diylib.sysgpio["F1"]["DAT"]<1000:
            send_data(webssdset.diylib.syspam["GETTIME"],webssdset.diylib.sysgpio["F1"]["DAT"],webssdset.diylib.sysgpio["F2"]["DAT"])
        else:
            send_data(webssdset.diylib.syspam["GETTIME"],0,0)
            print("DHT fial link ...")
    #=== wifi led flash mode ===
    if wifiled_flag==0:
        wifiled(1)# off led link ok
    elif wifiled_flag==1:
        wifiled(0)# on led link fail
    elif wifiled_flag==2:
        wifiled(not wifiled.value())#flash LED
    elif wifiled_flag==3:
        if (tick_count%8)<4:
            wifiled(not wifiled.value())#flash LED
        else:
            wifiled(1)# off led link ok
    else:
        wifiled(1)# off led 
    tt=now().split("-")
    tday=tt[1].split(":")
    thh=tday[0]+tday[1]
    if webssdset.diylib.sysgpio["R1"]["AUTO"]==1:
        if int(thh)>int(webssdset.diylib.sysgpio["R1"]["ST"]) and int(thh)<int(webssdset.diylib.sysgpio["R1"]["END"]):
            webssdset.diylib.sysgpio["R1"]["DAT"]=0#on
        else:
            webssdset.diylib.sysgpio["R1"]["DAT"]=1#off
    if webssdset.diylib.sysgpio["R2"]["AUTO"]==1:
        if int(thh)>int(webssdset.diylib.sysgpio["R2"]["ST"]) and int(thh)<int(webssdset.diylib.sysgpio["R2"]["END"]):
            webssdset.diylib.sysgpio["R2"]["DAT"]=0#on
        else:
            webssdset.diylib.sysgpio["R2"]["DAT"]=1#off
    if webssdset.diylib.sysgpio["R3"]["AUTO"]==1:
        if int(thh)>int(webssdset.diylib.sysgpio["R3"]["ST"]) and int(thh)<int(webssdset.diylib.sysgpio["R3"]["END"]):
            webssdset.diylib.sysgpio["R3"]["DAT"]=0#on
        else:
            webssdset.diylib.sysgpio["R3"]["DAT"]=1#off
    webssdset.diylib.R1(webssdset.diylib.sysgpio["R1"]["DAT"])
    webssdset.diylib.R2(webssdset.diylib.sysgpio["R2"]["DAT"])
    webssdset.diylib.R3(webssdset.diylib.sysgpio["R3"]["DAT"])
def do_connect():
    global wifiled_flag
    global wifiled
    if not sta.isconnected():
        print('Connecting to network...')
        sta.active(True)
        sta.connect(webssdset.diylib.syspam["SSID"], webssdset.diylib.syspam["PASSWORD"])
        time.sleep(WAIT_FOR_CONNECT)     
        if sta.isconnected():
            wifiled_flag=3
            print('Network connected!')
def send_data(dattime,dattm,datrh):
    if sta.isconnected():
        wifi_count=0
        wifiled_flag=3
        print('Sending data...')
        #url='%s&field1=%s&field2=%s&field3=%s' %(config.URL, dattime, dattm, datrh)
        url = '%s%s'%(webssdset.diylib.syspam["UPLOADURL"],webssdset.diylib.syspam["LINKID"])
        if not (datrh==0 and dattm==0):
            if webssdset.diylib.sysgpio["F1"]["ENB"]==1:
                url='%s&%s=%.2f'%(url,webssdset.diylib.sysgpio["F1"]["TYPE"],webssdset.diylib.sysgpio["F1"]["DAT"])
            if webssdset.diylib.sysgpio["F2"]["ENB"]==1:
                url='%s&%s=%.2f'%(url,webssdset.diylib.sysgpio["F2"]["TYPE"],webssdset.diylib.sysgpio["F2"]["DAT"])
            if webssdset.diylib.sysgpio["F3"]["ENB"]==1:
                url='%s&%s=%.2f'%(url,webssdset.diylib.sysgpio["F3"]["TYPE"],webssdset.diylib.sysgpio["F3"]["DAT"])
        print('=>'+url)
        try:
            cmdstr = http_get(url)
            reqcommm(cmdstr)
            print("upload ok!")
        except:
            print("wifi week link ...")
    else:
        wifi_count=wifi_count+1
        if wifi_count>5:
            wifi_count=0
            machine.reset()
        wifiled_flag=2
        print('wifi off link send data Fail...')
def now():
    utc_epoch=time.mktime(time.localtime())
    Y,M,D,H,m,S,ms,W=time.localtime(utc_epoch + 28800)#add 8hr for Taiwan time
    t="%s%s%s-%02d:%02d:%02d"%(Y,M,D,H,m,S)
    return t
def getdht22():
	# === get wtm ===
    try:
        temp =float(webssdset.diylib.GETBH1750.getds18x20())
    except:
        temp=100
        #hum=100
    #print('Humidity: {}%'.format(hum))
    print('WTM: %s'%str(temp))
	# === get lux === 
    try:
        hum = int(webssdset.diylib.GETBH1750.getlux())
    except:
        #temp=100
        hum=100
    print('Lux: %s'%str(hum))
    return temp,hum
def reqcommm(recomm):
    ss=recomm.split('\n')
    jcmd ="pass ..."
    for i in ss:
        if i.find("SAVEPAM")>=0:
            writejpam("JSYSGPIO.json",webssdset.diylib.sysgpio)
            break
        if i.find("{")>=0:
            jcmd=i
            break
    if jcmd.find("pass")==-1:
        print(jcmd, end='\n')
        jobj = ujson.loads(jcmd)
        for i in jobj:
            if i in webssdset.diylib.sysgpio:
                for j in jobj[i]:
                    webssdset.diylib.sysgpio[i][j]=jobj[i][j];
            elif i in webssdset.diylib.syspam:
                webssdset.diylib.syspam[i]=jobj[i]
    else:
        print(jcmd)
def http_get(url):
    global socket
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    cmdstr=""
    while True:
        data = s.recv(100)
        if data:
            cmdstr = cmdstr + str(data, 'utf8');
        else:
            break
    s.close()
    return cmdstr
def main():
    global webssdset
    global wifiled_flag
    global wifiled
    
    wifiled_flag=0
    webssdset.diylib.syspam=loadjpam("JSYSPAM.json")
    #webssdset.syspam = SYSPAM
    print(webssdset.diylib.syspam)
    webssdset.diylib.sysgpio=loadjpam("JSYSGPIO.json")
    #webssdset.sysgpip = SYSGPIO
    print(webssdset.diylib.sysgpio)
    
    tim.deinit()
    wifiled(1)# power on off LED
    inchksw=chksw()
    print("/n[chksw = %d ]"%inchksw)
    
    if inchksw==1:
        tim.init(period=500, mode=Timer.PERIODIC, callback=tick)#0.5 sec interval IRQ
        print("RUN Timer IRQ Enable ...")
    else:
        tim.deinit()
        print("Timer IRQ Disable ...")
        time.sleep(WAIT_FOR_CONNECT)
        print("Goto set wifi AP 192.168.4.1 ...")
        webssdset.setap()
    print("start link check ...")
    time.sleep(15)     
    if not sta.isconnected():
        print("Fail link!!!")
        while not sta.isconnected():
            wifiled_flag=2
            do_connect()
    else:
        print("Redy link...")
        wifiled_flag=3
        print("poweron_time:%s" %str(time.localtime()))
        try:
            ntptime.settime()
        except:
            print("NPT time link Fail ...")    
        print("setup_time%s" %str(time.localtime()))
    tmoffsetdat=webssdset.diylib.sysgpio["F1"]["OFFSET"]
    rhoffsetdat=webssdset.diylib.sysgpio["F2"]["OFFSET"]
    while True:
        webssdset.main()
        pass
if __name__ == '__main__':
    main()



