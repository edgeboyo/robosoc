import os
import threading
import time

import RPi.GPIO as GPIO

from fan import runFan, norm, turbo

os.system("sudo pigpiod")
time.sleep(1)  # do not remove apparently
import pigpio

GPIO.setmode(GPIO.BCM)
sonic_sensors = {"front": (2, 3), "left": (4, 17), "right": (27, 22)}

ESC1 = 18  # Connect the ESC in this GPIO pin
ESC2 = 24  # Connect the ESC of second motor to this GPIO pin

pi = pigpio.pi();
pi.set_servo_pulsewidth(ESC1, 0)
pi.set_servo_pulsewidth(ESC2, 0)

for pin_tuple in sonic_sensors.values():
    GPIO.setup(pin_tuple[0], GPIO.OUT)
    GPIO.setup(pin_tuple[1], GPIO.IN)

print("Sonic sensors set up!")

max_value = 2000
min_value = 1000


class DistanceWrapper:
    def __init__(self):
        self.keys = {"front": 0, "left": 1, "right": 2}
        self.distances = [1000, 1000, 1000]


dwrapper = DistanceWrapper()


def distance(pin):
    global dwrapper
    while True:
        GPIO.output(sonic_sensors[pin][0], True)
        time.sleep(0.00001)  # was 0.00001 now it's 100Hz to save cpu usage.
        GPIO.output(sonic_sensors[pin][0], False)
        StartTime = time.time()
        StopTime = time.time()
    
        while GPIO.input(sonic_sensors[pin][1]) == 0:
            StartTime = time.time()
    
        while GPIO.input(sonic_sensors[pin][1]) == 1:
            StopTime = time.time()
    
        dwrapper.distances[dwrapper.keys[pin]] = (StopTime - StartTime) * 34300 / 2
        time.sleep(0.001)


if __name__ == "__main__":
    try:
        front_thread = threading.Thread(target=distance, args="front")
        left_thread = threading.Thread(target=distance, args="left")
        right_thread = threading.Thread(target=distance, args="right")
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
        front_thread.start()
        left_thread.start()
        right_thread.start()
        last_known_pos = 0 # 1 for front, 2 for left, 3 for right
        while True:
            distf = dwrapper.distances[0]
            distl = dwrapper.distances[1]
            distr = dwrapper.distances[2]
            print(distl, distf, distr)
            positions = [1, 2, 3]

            if (distf <= 110) or (distr <= 110) or (distl <= 110):
                pos = [distf, distl, distr]
                last_known_pos = positions[pos.index(min(pos))]

            if (distl <= 15) & (distf <= 15) & (distr <= 15):
                pi.set_servo_pulsewidth(ESC1, 2000)
                pi.set_servo_pulsewidth(ESC2, 2000)
                turbo()
            elif distf <= 110:
                pi.set_servo_pulsewidth(ESC1, 1600)
                pi.set_servo_pulsewidth(ESC2, 1600)
            elif (distf >= 110) & (distl <= 110):
                pi.set_servo_pulsewidth(ESC1, 1460)
                pi.set_servo_pulsewidth(ESC2, 1550)
            elif (distf >= 110) & (distr <= 110):
                pi.set_servo_pulsewidth(ESC1, 1540)
                pi.set_servo_pulsewidth(ESC2, 1460)
            else:
                if last_known_pos == 1:
                    pi.set_servo_pulsewidth(ESC1, 1460)
                    pi.set_servo_pulsewidth(ESC2, 1550)
                else:
                    pi.set_servo_pulsewidth(ESC1, 1540)
                    pi.set_servo_pulsewidth(ESC2, 1460)
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        GPIO.cleanup()
        os.system("sudo killall pigpiod")
        pi.stop()
