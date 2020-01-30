import os, time

os.system("sudo pigiod")
time.sleep(1)
import pigpio

FAN1 = 12 #Connect fan to this

pi = pigpio.pi()
pi.set_servo_pulsewidth(FAN1, 1000)
time.sleep(5)
pi.set_servo_pulsewidth(FAN1, 1200)

try:
    while True:
        pass
except KeyboardInterrupt:
    os.system("sudo killall pigpiod")
