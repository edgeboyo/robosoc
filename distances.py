import os
import RPi.GPIO as GPIO
import time
# os.system("sudo pigpiod")
# time.sleep(1) # do not remove apparently
# import pigpio

GPIO.setmode(GPIO.BCM)
sonic_sensors = {"front": (2, 3), "left": (4, 17), "right": (27, 22)}

for pin_tuple in sonic_sensors.values():
    GPIO.setup(pin_tuple[0], GPIO.OUT)
    GPIO.setup(pin_tuple[1], GPIO.IN)

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
            distf = distance("front")
            distr = distance("right")
            distl = distance("left")
            print("{} {} {}".format(distl, distf, distr))
            time.sleep(0.5)
    except KeyboardInterrupt:
        GPIO.cleanup()
        # os.system("sudo killall pigpiod")
        # pi.stop()
