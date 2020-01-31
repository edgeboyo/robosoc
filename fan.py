import os, time

os.system("sudo pigpiod")
time.sleep(1)
import pigpio

FAN1 = 12 #Connect fan to this

pi = pigpio.pi()

def runFan():
    pi.set_servo_pulsewidth(FAN1, 1000)
    #time.sleep(5)
    #pi.set_servo_pulsewidth(FAN1, 1200)
    time.sleep(2)
    pi.set_servo_pulsewidth(FAN1, 1050)
    print("Fan setup complete!")
#time.sleep(1)
#pi.set_servo_pulsewidth(FAN1, 1200)
#pi.set_servo_pulsewidth(FAN1, 1650)

def norm():
    pi.set_servo_pulsewidth(FAN1, 1050)
    
def turbo():
    pi.set_servo_pulsewidth(FAN1, 1600)

if __name__ == "__main__":
    runFan()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        os.system("sudo killall pigpiod")
