import os, time, threading, queue
import RPi.GPIO as GPIO

import fan

os.system("sudo pigpiod")
time.sleep(1)  # do not remove apparently
import pigpio

# constants

GPIO.setmode(GPIO.BCM)
sonic_sensors = {"front": (2, 3), "left": (4, 17), "right": (27, 22)}

for pin_tuple in sonic_sensors.values():
    GPIO.setup(pin_tuple[0], GPIO.OUT)
    GPIO.setup(pin_tuple[1], GPIO.IN)

ESC1 = 18  # Connect the ESC in this GPIO pin
ESC2 = 24  # Connect the ESC of second motor to this GPIO pin

max_value = 2000
min_value = 1000

"""
STATE OUTLINE
STATE -1: pre battle state
STATE 0: Enemy is in front but not too close
STATE 1/1.5: Enemy is within view of left or right sensors so will turn to see it
STATE 2: Enemy is out of view of all sensors
STATE 3: Enemy is within turbo range
"""

class Bobot():

    def __init__(self):
        self.state = -1
        self.last_known_pos = 0 # 1 for front, 2 for left, 3 for right

        self.pi = pigpio.pi()
        self.pi.set_servo_pulsewidth(ESC1, 0)
        self.pi.set_servo_pulsewidth(ESC2, 0)

        self.front_queue = queue.Queue();
        self.left_queue = queue.Queue();
        self.right_queue = queue.Queue();
        
        self.front_distance_thread = threading.Thread(target=self.check_distance, args=("front", self.front_queue))
        self.left_distance_thread = threading.Thread(target=self.check_distance, args=("left", self.left_queue))
        self.right_distance_thread = threading.Thread(target=self.check_distance, args=("right", self.right_queue))
        self.state_thread = threading.Thread(target=self.change_state(self.front_queue, self.left_queue, self.right_queue))
        
        self.arm_motors()

    def go_left(self):
        self.pi.set_servo_pulsewidth(ESC1, 1460)
        self.pi.set_servo_pulsewidth(ESC2, 1550)

    def go_right(self):
        self.pi.set_servo_pulsewidth(ESC1, 1550)
        self.pi.set_servo_pulsewidth(ESC2, 1460)

    def start_battle(self):
        self.front_distance_thread.start()
        self.left_distance_thread.start()
        self.right_distance_thread.start()
        self.state_thread.start()
        
        while True:
            if self.state == 0:
                self.pi.set_servo_pulsewidth(ESC1, 1600)
                self.pi.set_servo_pulsewidth(ESC2, 1600)
            elif self.state == 1:
                self.go_left()
            elif self.state == 1.5:
                self.go_right()
            elif self.state == 2:
                if self.last_known_pos == 3:
                    self.go_right()
                if self.last_known_pos == 2:
                    self.go_left()
            elif self.state == 3:
                self.pi.set_servo_pulsewidth(ESC1, 2000)
                self.pi.set_servo_pulsewidth(ESC2, 2000)
                fan.turbo()

        time.sleep(0.001)

    def check_distance(self, pin, q):
        while True:
            GPIO.output(sonic_sensors[pin][0], True)
            time.sleep(0.00001)
            GPIO.output(sonic_sensors[pin][0], False)
            StartTime = time.time()
            StopTime = time.time()

            while GPIO.input(sonic_sensors[pin][1]) == 0:
                StartTime = time.time()

            while GPIO.input(sonic_sensors[pin][1]) == 1:
                StopTime = time.time()

            q.append((StopTime - StartTime) * 34300 / 2)
            time.sleep(0.001)

    def change_state(self, f, l, r):
        # no clue what happens if theres nothing on the queue, probably just None
        fdist = f.get()
        ldist = l.get()
        rdist = r.get()

        positions = [1, 2, 3]

        if (fdist <= 150) or (rdist <= 150) or (ldist <= 150):
            pos = [fdist, ldist, rdist]
            self.last_known_pos = positions[pos.index(min(pos))]

        if fdist and fdist <= 150:
            # belt forwards but not full speed if it sees something in front
            self.state = 0
            f.remove(f[0])
            if ldist:
                l.remove(l[0])
            if rdist:
                r.remove(r[0])

        if (rdist <= 150 or ldist <= 150) and fdist >= 150:
            if ldist <= 150:
                self.state = 1
            elif rdist <= 150:
                self.state = 1.5

        if fdist > 150 and ldist > 150 and rdist > 150:
            self.state = 2

        if fdist <= 20 and ldist <= 20 and rdist <= 20:
            self.state = 3


    def arm_motors(self):
        self.pi.set_servo_pulsewidth(ESC1, 0)
        self.pi.set_servo_pulsewidth(ESC2, 0)
        time.sleep(1)
        self.pi.set_servo_pulsewidth(ESC1, max_value)
        self.pi.set_servo_pulsewidth(ESC2, max_value)
        time.sleep(1)
        self.pi.set_servo_pulsewidth(ESC1, min_value)
        self.pi.set_servo_pulsewidth(ESC2, min_value)
        time.sleep(1)
        self.pi.set_servo_pulsewidth(ESC1, 1500)
        self.pi.set_servo_pulsewidth(ESC2, 1500)
        print("Motors armed")
        fan.runFan()
        fan.norm()
        print("Fan calibrated")

if __name__ == "__main__":
    bobot = Bobot()
    input("press enter to start battle")
    try:
        bobot.start_battle()
    except KeyboardInterrupt:
        GPIO.cleanup()
        os.system("sudo killall pigpiod")
        bobot.pi.stop()
