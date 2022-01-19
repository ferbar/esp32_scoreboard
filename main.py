from machine import Pin
from machine import I2C
from time import sleep
import pca9685
import socket
import sys

statusLed = Pin(2, Pin.OUT)
value = 0

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)

print("I2C init done")

def I2CScan(querystring):
    print("I2CScan %s" % querystring)
    ret=""
    devices = i2c.scan()
    for device in devices:
        ret+=hex(device) + " "
    return ret

addrMapping=[]
duty=4096

def setChar(pos, c):
    print("setChar %d %s" %(pos,c))
    board=int(pos/2)
    digit=int(pos%2)
    print("   board=%d digit=%d boardlen=%d" % (board, digit, len(addrMapping) ))
    #if board < len(addrMapping) ... let it throw exception
    
    for i in range (0,7):
        port=i+(digit*8)
        value=0 if c=='0' else 4095
        print("setting %d to %d" % (port, value) )
        addrMapping[board].duty(port, value)
    

def setLeds(querystring):
    print("setLeds %s" % querystring)
    args=querystring.split('&')
    pos=0
    s=""
    for arg in args:
        kv=arg.split("=")
        if kv[0]=="p":
            print("Setting pos to %s" % kv[1])
            pos=int(kv[1])
        elif kv[0]=='s':
            print("print string %s" % kv[1])
            s=kv[1]
            for c in s:
                setChar(pos, c)
                pos+=1
    
    return ( "setLeds@%d[%s]" % (pos,s) )
    

# /initleds?41&43&40&42
def initLeds(querystring):
    print("initLeds %s" % querystring)
    global addrMapping
    addrMapping=[]
    for tuple in querystring.split('&'):
        print("---- %s" % tuple)
        kv=tuple.split("=")
        if(len(kv) == 1):
            pca=pca9685.PCA9685(i2c, int(kv[0]))
            pca.freq(1000)
            addrMapping.append(pca)
        else:
            print("some key value pair: %s=%s" % (kv[0], kv[1]) )
    return "init done len=%d" % len(addrMapping)

# start HTTP Server
import socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)
print('listening on', addr)

while True:
    try:
        conn, addr = s.accept()
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        request = request.decode('utf-8')
        # print('Content = [[%s]]\r\n' % request)
        split=request.split(' ')
        method=str(split[0])
        print("  method: %s" % method);
        url=(split[1])
        print("  url=%s" % url);
        split=url.split('?')
        if(len(split) > 1):
            url=str(split[0])
            print("  url=%s" % url);
            querystring=str(split[1])
            print("  querystring=%s" % querystring)
        print("====\r\n");
        response = "reponse"
        if(method=="GET" and url=="/setleds"):
            response=setLeds(querystring)
        elif(method=="GET" and url=="/initleds"):
            response=initLeds(querystring)
        elif(method=="GET" and url=="/i2cscan"):
            response=I2CScan(querystring)
        elif(method=="GET" and url=="/favicon.ico"):
            response="favicon"
        else:
            print("invalid url [%s] [%s]" % (method, url))
            respones="invalid url [%s] [%s]" % (method, url)
    
    except Exception as e:
        # print(e)
        response=str(e)
        print(repr(e))
        sys.print_exception(e)

#    led_on = request.find('/?led=on')
#    led_off = request.find('/?led=off')
  
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()
    print("\r\n================\r\n");
    
    statusLed.value(not statusLed.value())
  