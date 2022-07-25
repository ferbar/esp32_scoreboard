from machine import Pin
from time import sleep
print("CTRL+C to abort...")
led = Pin(2, Pin.OUT)
connected=False
import network

sta_if = network.WLAN(network.STA_IF)
sta_if.active()
sta_if.connect('foo','bar')

while not connected:
    for i in range(20):
        if connected != sta_if.isconnected():
            print("Wifi connected")
            print(sta_if.ifconfig())
            connected = True
            break

        led.value(not led.value())
        sleep(0.5)    
    if connected:
        break
    sta_if.disconnect()
    sleep(1)
    sta_if.active()
    sta_if.connect('foo','bar')    

led.value(False)
for i in range(3):
    led.value(True)
    sleep(0.2)
    led.value(False)
    sleep(0.2)

if not sta_if.isconnected():
   print("Wifi not connected")

sta_if=False

import scoreboard
