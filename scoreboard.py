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
duty=4095

charSegments = [
    0B11111100,  # 0
    0B01100000,  # 1
    0B11011010,  # 2
    0B11110010,  # 3
    0B01100110,  # 4
    0B10110110,  # 5
    0B10111110,  # 6
    0B11100000,  # 7
    0B11111110,  # 8
    0B11100110,  # 9
    0B11101110,  # A
    0B00111110,  # b
    0B10011100,  # C
    0B01111010,  # d
    0B10011110,  # E
    0B10001110   # F
]

def setDot(pos, on):
    global duty
    print("setDot %d %d" %(pos,on))
    board=int(pos/2)
    digit=int(pos%2)
    print("   board=%d digit=%d boardlen=%d" % (board, digit, len(addrMapping) ))
    value=duty if on else 0
    port=7+(digit*8)
    print("setting %d to %d" % (port, value) )
    addrMapping[board].duty(port, value)

# char int(0) .. int(15)
def setChar(pos, c, hex=False):
    global duty
    print("setChar %d %d" %(pos,c))
    
    board=int(pos/2)
    digit=int(pos%2)
    print("   board=%d digit=%d boardlen=%d" % (board, digit, len(addrMapping) ))
    #if board < len(addrMapping) ... let it throw exception
    
    if not hex:
        if c < 0 or c > len(charSegments):
            raise Exception("invalid char %d" % c)
        charSegment=charSegments[c]
        r = 7
    else:
        charSegment = c
        r = 8
    
    for i in range(r):
        port=i+(digit*8)
        value=duty if charSegment & ( 1 << (7-i) ) else 0
        print("setting %d to %d" % (port, value) )
        addrMapping[board].duty(port, value)

# char int(0) .. int(15)
def setDuty(querystring):  
    global duty
    print("setDuty %d" %(duty))
    d = int(querystring)
    if d > 4095:
        d = 4095
    if d < 0:
        d = 0
    duty=d
    return ( "setDutys@%d" % (duty) )

# p ... startpos
# s ... string "123456" " " für punkt löschen "." für punkt setzen
def setLeds(querystring):
    print("setLeds %s" % querystring)
    args=querystring.split('&')
    pos=0
    s=""
    for arg in args:
        kv=arg.split("=")
        if kv[0]=="p":
            print("  Setting pos to %s" % kv[1])
            pos=int(kv[1])
        elif kv[0]=="b":
            print("  Setting duty to %s" % kv[1])                        
            setDuty(kv[1])
        elif kv[0]=="c":
            print("  setting hex string %s" % kv[1])
            setChar(pos, int(kv[1],0), hex=True)
            pos += 1
        elif kv[0]=='s':
            print("  print string %s" % kv[1])
            s=kv[1]
            for c in s:
                if c == '_':
                    setDot(pos, False)
                elif c == '.':
                    setDot(pos, True)
                else:
                    setChar(pos, ord(c) - ord('0'))
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
            pca=pca9685.PCA9685(i2c, int(kv[0],0))
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
        querystring=''
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
        elif(method=="GET" and url=="/setbrightness"):
            response=setDuty(querystring)
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
  