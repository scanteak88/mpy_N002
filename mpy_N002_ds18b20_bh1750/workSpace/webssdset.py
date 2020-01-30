import diylib
import os
Pin =diylib.Pin
socket =diylib.socket
time =diylib.time
ujson =diylib.ujson
diylib.gc.collect()

wifiled=diylib.wifiled#D4
sta=diylib.network.WLAN(diylib.network.STA_IF)
sta.active(True)
errhtml=diylib.errhtml
setaphtml=diylib.setaphtml
form=diylib.form
passform=diylib.passform
gpiohtml=diylib.gpiohtml
chkurl=diylib.chkurl
loadjpam =diylib.loadjpam
writejpam=diylib.writejpam 
def reloadhtml(cs):    
    xform=form%(diylib.syspam["SSID"],diylib.syspam["UPLOADURL"],diylib.syspam["LINKID"],diylib.syspam["UPLOADTIME"])
    cs.send(setaphtml % xform)
    cs.close()
def setap():
    ap = diylib.network.WLAN(diylib.network.AP_IF)
    ap.active(True)
    addr=socket.getaddrinfo('192.168.4.1', 80)[0][-1]
    s=socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(4)
    print('listening on', addr)
    wifiled(0)#LED on is link wifi ok
    while True:
        cs, addr=s.accept()
        print('client connected from', addr)
        data=cs.recv(1024)
        request=str(data,'utf8')
        print(request, end='\n')
        if request.find('update_ap?') >= 4:
            para=request[request.find('ssid='):request.find(' HTTP/')]
            xssid=para.split('&')[0].split('=')[1]
            xpwd=para.split('&')[1].split('=')[1]
            ssid = chkurl(xssid)
            pwd = chkurl(xpwd)
            sta.connect(ssid,pwd)
            time.sleep(diylib.WAIT_FOR_CONNECT)
            if sta.isconnected():
                diylib.syspam["SSID"]=ssid
                diylib.syspam["PASSWORD"]=pwd
                print('Connected:IP=',sta.ifconfig()[0])
                cs.send(passform % sta.ifconfig()[0])#cs.close()
                writejpam("JSYSPAM.json",diylib.syspam)
                time.sleep(diylib.WAIT_FOR_CONNECT)
                wifiled(1)#LED off is link wifi ok
            else:
                wifiled(0)#LED on is link wifi fail
                reloadhtml(cs)
        elif request.find('update_url?') >= 4:
            para=request[request.find('UPLOADURL='):request.find(' HTTP/')]
            xpara=chkurl(para)
            xUPLOADURL=xpara.split('&')[0].split('=')[1]
            xLINKID=xpara.split('&')[1].split('=')[1]
            xUPLOADTIME=xpara.split('&')[2].split('=')[1]
            diylib.syspam["UPLOADURL"] = xUPLOADURL+"="
            diylib.syspam["LINKID"] = xLINKID
            diylib.syspam["UPLOADTIME"] = int(xUPLOADTIME)
            wifiled(1)#LED off is link wifi ok
            reloadhtml(cs)
            writejpam("JSYSPAM.json",diylib.syspam)
            time.sleep(diylib.WAIT_FOR_CONNECT)
        else:
            reloadhtml(cs)
    s.close()
def workgpio():
    print("showgpio=",diylib.sysgpio)
    pins=[Pin(i, Pin.OUT) for i in (12,13,14,15)]
    addr=socket.getaddrinfo(str(sta.ifconfig()[0]), 80)[0][-1]
    s=socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    print('listening on', addr)
    while True:
        cs, addr=s.accept()
        print('client connected from', addr)
        data=cs.recv(1024)
        xrequest=str(data,'utf8')
        ss=xrequest.split('\n')
        for i in ss:
            if i.find("GET")>=0:
                print(">>"+i)
                request=i
                break
        print(request, end='\n')
        if request.find('/SETGPIO?')>0:  
            rows=[]
            for p in pins:
                set='?%s=1' % str(p)
                reset='?%s=0' % str(p)
                print("chk=",set,reset,request.find(set),request.find(reset))
                if request.find(set)>=0:
                    if str(p).find("Pin(12)")>=0:
                        diylib.sysgpio["R1"]["DAT"]=1
                    elif str(p).find("Pin(13)")>=0:
                        diylib.sysgpio["R2"]["DAT"]=1
                    elif str(p).find("Pin(14)")>=0:
                        diylib.sysgpio["R3"]["DAT"]=1
                    elif str(p).find("Pin(15)")>=0:
                        diylib.sysgpio["R4"]["DAT"]=1
                    else:
                        pass
                    p.value(1)
                if request.find(reset)>=0:
                    if str(p).find("Pin(12)")>=0:
                        diylib.sysgpio["R1"]["DAT"]=0
                    elif str(p).find("Pin(13)")>=0:
                        diylib.sysgpio["R2"]["DAT"]=0
                    elif str(p).find("Pin(14)")>=0:
                        diylib.sysgpio["R3"]["DAT"]=0
                    elif str(p).find("Pin(15)")>=0:
                        diylib.sysgpio["R4"]["DAT"]=0
                    else:
                        pass
                    p.value(0)
                row="""<tr><td>%s</td><td>%d</td><td><a href='/SETGPIO?%s=1'>HIGH</a><a href='/SETGPIO?%s=0'>LOW</a></td></tr>"""
                rows.append(row % (str(p), p.value(), str(p), str(p)))
        elif request.find('/SETAUTO?')>=0:
            print("setupauto ...")
            ss1=request.split(' ')
            ss2=ss1[1].split('?')
            if ss2[1].find("Pin(12)")>=0:
                rkey="R1"
            elif ss2[1].find("Pin(13)")>=0:
                rkey="R2"
            elif ss2[1].find("Pin(14)")>=0:
                rkey="R3"
            elif ss2[1].find("Pin(15)")>=0:
                rkey="R4"
            else:
                rkey="00"
            if rkey in diylib.sysgpio:
                ss3=ss2[1].split('&')
                for apikey in ss3:
                    if "Pin" in apikey:
                        apivalue=apikey.split('=')
                        diylib.sysgpio[rkey]['DAT']=int(apivalue[1])
                    elif "AUTO" in apikey:
                        apivalue=apikey.split('=')
                        diylib.sysgpio[rkey]['AUTO']=int(apivalue[1])
                    elif "ST" in apikey:
                        apivalue=apikey.split('=')
                        diylib.sysgpio[rkey]['ST']=apivalue[1] 
                    elif "END" in apikey:
                        apivalue=apikey.split('=')
                        diylib.sysgpio[rkey]['END']=apivalue[1] 
                    elif "INTERVAL" in apikey:
                        apivalue=apikey.split('=')
                        diylib.sysgpio[rkey]['INTERVAL']=apivalue[1] 
            rows=[]
            for p in pins:
                row="""<tr><td>%s</td><td>%d</td><td><a href='/SETGPIO?%s=1'>HIGH</a><a href='/SETGPIO?%s=0'>LOW</a></td></tr>"""
                rows.append(row % (str(p), p.value(), str(p), str(p)))
        elif request.find('/SAVEPAM?')>=0:
            print("savepam ...")
            writejpam("JSYSGPIO.json",diylib.sysgpio)
            rows=[]
            for p in pins:
                row="""<tr><td>%s</td><td>%d</td><td><a href='/SETGPIO?%s=1'>HIGH</a><a href='/SETGPIO?%s=0'>LOW</a></td></tr>"""
                rows.append(row % (str(p), p.value(), str(p), str(p)))
            row="""<tr>%s</tr>"""
            rows.append(row % (str(diylib.sysgpio)))
        elif request.find('/LOADPAM?')>=0:
            rows=[]
            row="""<tr>%s</tr>"""
            rows.append(row % (str(diylib.sysgpio)))
        else:
            print("ERR3...")
            rows=[]
            for p in pins:
                row="""<tr><td>%s</td><td>%d</td><td><a href='/SETGPIO?%s=1'>HIGH</a><a href='/SETGPIO?%s=0'>LOW</a></td></tr>"""
                rows.append(row % (str(p), p.value(), str(p), str(p)))
        response = gpiohtml % '\n'.join(rows)
        cs.send(response)
        cs.close()
        print(diylib.sysgpio)
        print("RSW=[R1:%d ,R2:%d ,R3:%d ,R4:%d ]"%(diylib.sysgpio["R1"]["DAT"],diylib.sysgpio["R2"]["DAT"],diylib.sysgpio["R3"]["DAT"],diylib.sysgpio["R4"]["DAT"]))
        print("RAUTO=[R1:%d ,R2:%d ,R3:%d ,R4:%d ]"%(diylib.sysgpio["R1"]["AUTO"],diylib.sysgpio["R2"]["AUTO"],diylib.sysgpio["R3"]["AUTO"],diylib.sysgpio["R4"]["AUTO"]))
    s.close()
def main():
    print('Connecting to AP ...')
    print("showgpio=",diylib.sysgpio)
    time.sleep(diylib.WAIT_FOR_CONNECT)
    while True:
        if not sta.isconnected():
            setap()
        else:
            ipadd = str(sta.ifconfig()[0])
            diylib.syspam["IPADD"] = ipadd
            print('Connected:IP=', ipadd)
            workgpio()
if __name__ == '__main__':
    pass
