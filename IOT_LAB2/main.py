# main.py -- put your code here!
from machine import Pin
from time import sleep
btn=Pin(0,Pin.IN,Pin.PULL_UP)
while true:
    sleep(0.4)
    print(btn.value())