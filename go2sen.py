import os
import RPi.GPIO as GPIO
import time
os.system("sudo pigpiod")
time.sleep(1) # do not remove apparently
import pigpio

GPIO.setmode(GPIO.BCM)
sonic_sensors = {"left": (4, 17), "right": (27, 22)}

ESC1=18  #Connect the ESC in this GPIO pin 
ESC2=24  #Connect the ESC of second motor to this GPIO pin

pi = pigpio.pi();
pi.set_servo_pulsewidth(ESC1, 0) 
pi.set_servo_pulsewidth(ESC2, 0)

for pin_tuple in sonic_sensors.values():
    GPIO.setup(pin_tuple[0], GPIO.OUT)
    GPIO.setup(pin_tuple[1], GPIO.IN)

print("Sonic sensors set up!")

import fan

from fan import runFan
from fan import norm
from fan import turbo

max_value = 2000
min_value = 1000

def distance(pin):
    GPIO.output(sonic_sensors[pin][0], True)
    time.sleep(0.00001)# was 0.00001 now it's 100Hz to save cpu usage.
    GPIO.output(sonic_sensors[pin][0], False)
    StartTime = time.time()
    StopTime = time.time()

    while GPIO.input(sonic_sensors[pin][1]) == 0:
        StartTime = time.time()

    while GPIO.input(sonic_sensors[pin][1]) == 1:
        StopTime = time.time()

    return (StopTime - StartTime) * 34300 / 2

if __name__ == "__main__":
    try:
        pi.set_servo_pulsewidth(ESC1, 0)
        pi.set_servo_pulsewidth(ESC2, 0)
        time.sleep(1)
        pi.set_servo_pulsewidth(ESC1, max_value)
        pi.set_servo_pulsewidth(ESC2, max_value)
        time.sleep(1)
        pi.set_servo_pulsewidth(ESC1, min_value)
        pi.set_servo_pulsewidth(ESC2, min_value)
        time.sleep(1)
        pi.set_servo_pulsewidth(ESC1, 1500)
        pi.set_servo_pulsewidth(ESC2, 1500)
        print("Motors armed")
        runFan()
        norm()
        print("Calibration  complete time to run!")
        input("Enter key to start battle...")
        #print(distl, distf, distr)
        last = 'f'
        while True:
            #distf = distance("front")
            distr = distance("right")
            distl = distance("left")
            print(distl, distr)

            if (distl <= 20) and (distr <= 20):
                pi.set_servo_pulsewidth(ESC1, 2000)
                pi.set_servo_pulsewidth(ESC2, 2000)
                turbo()
            elif (distl <= 120) and (distr <= 120):
                pi.set_servo_pulsewidth(ESC1, 1600)
                pi.set_servo_pulsewidth(ESC2, 1600)
                last = 'f'
            elif (distl <= 120):
                pi.set_servo_pulsewidth(ESC1, 1550)
                pi.set_servo_pulsewidth(ESC2, 1600)
                last = 'l'
            elif (distr <= 120):
                pi.set_servo_pulsewidth(ESC1, 1600)
                pi.set_servo_pulsewidth(ESC2, 1550)
                last = 'r'
            else:
                if (last == 'f'):
                    pi.set_servo_pulsewidth(ESC1, 1600)
                    pi.set_servo_pulsewidth(ESC2, 1600)   
                elif (last == 'l'):
                    pi.set_servo_pulsewidth(ESC1, 1550)
                    pi.set_servo_pulsewidth(ESC2, 1600)
                elif (last == 'r'):
                    pi.set_servo_pulsewidth(ESC1, 1600)
                    pi.set_servo_pulsewidth(ESC2, 1550)
                

            time.sleep(0.0001)
    except KeyboardInterrupt:
        GPIO.cleanup()
        os.system("sudo killall pigpiod")
        pi.stop()
