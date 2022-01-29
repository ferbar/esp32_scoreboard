from machine import Pin
from time import sleep
print("CTRL+C to abort...")
led = Pin(2, Pin.OUT)
connected=False
import network
sta_if = network.WLAN(network.STA_IF)

for i in range(10):
    if connected != sta_if.isconnected():
        print("Wifi connected")
        print(sta_if.ifconfig())
        connected = True
    
    led.value(not led.value())
    sleep(0.5)

if not sta_if.isconnected():
   print("Wifi not connected")

sta_if=False

import scoreboard