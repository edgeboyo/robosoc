import RPi.GPIO as GPIO
import time
import os
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

max_value = 2000
min_value = 1000

def distance(pin):
    GPIO.output(sonic_sensors[pin][0], True)
    time.sleep(0.00001)
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
        while True:
            dist = distance("front")
            print(dist)
            if distance <= 150:
                pi.set_servo_pulsewidth(ESC, 1000)
                pi.set_servo_pulsewidth(ESC2, 1000)
            else:
                pi.set_servo_pulsewidth(ESC, 0)
                pi.set_servo_pulsewidth(ESC2, 0)
            time.sleep(0.5)
    except KeyboardInterrupt:
        GPIO.cleanup()
        pi.stop()
