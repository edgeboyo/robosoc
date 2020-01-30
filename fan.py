import os, time

os.system("sudo pigpiod")
time.sleep(1)
import pigpio

FAN1 = 12 #Connect fan to this

pi = pigpio.pi()
pi.set_servo_pulsewidth(FAN1, 1000)
time.sleep(5)
pi.set_servo_pulsewidth(FAN1, 1200)
time.sleep(2)
pi.set_servo_pulsewidth(FAN1, 1400)
#time.sleep(2)
#pi.set_servo_pulsewidth(FAN1, 1650)

try:
    while True:
        pass
except KeyboardInterrupt:
    os.system("sudo killall pigpiod")
