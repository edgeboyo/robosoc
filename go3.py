import os
import RPi.GPIO as GPIO
import time
os.system("sudo pigpiod")
time.sleep(1) # do not remove apparently
import pigpio

GPIO.setmode(GPIO.BCM)
sonic_sensors = {"front": (2, 3), "left": (4, 17), "right": (27, 22)}

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
        print("Calibration  complete time to run!")
        input("Enter key to start battle...")
        while True:
            distf = distance("front")
            distr = distance("right")
            distl = distance("left")
            print(distl, distf, distr)
            if distf <= 150:
                pi.set_servo_pulsewidth(ESC1, 1600)
                pi.set_servo_pulsewidth(ESC2, 1600)
            elif (distf >= 150) & (distl <= 150):
                pi.set_servo_pulsewidth(ESC1, 1450)
                pi.set_servo_pulsewidth(ESC2, 1550)
                time.sleep(0.1)
            elif (distf >= 150) & (distr <= 150):
                pi.set_servo_pulsewidth(ESC1, 1550)
                pi.set_servo_pulsewidth(ESC2, 1450)
                time.sleep(0.1)
            else:
                pi.set_servo_pulsewidth(ESC1, 1450)
                pi.set_servo_pulsewidth(ESC2, 1550)
                time.sleep(0.1)
            time.sleep(0.001)
    except KeyboardInterrupt:
        GPIO.cleanup()
        os.system("sudo killall pigpiod")
        pi.stop()
