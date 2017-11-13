import ADC0832
import time
import RPi.GPIO as GPIO
import requests
import json

LedPin = 15    # pin15

def init():
        ADC0832.setup()
        GPIO.setup(LedPin, GPIO.OUT)   # Set LedPin's mode is output
        GPIO.output(LedPin, GPIO.HIGH) # Set LedPin high(+3.3V) to off led

def loop():
        prevRes = 0
        personCounter = 0
        print("Persons in: ", personCounter)
        data = json.dumps({'present':personCounter})
        r = requests.post('https://distributoricarsharing.appspot.com/pi_people',
                          data = data)
        currtime = time.time()
        nexttime = currtime + 10
        idletime = 0
        while True:
                GPIO.output(LedPin, GPIO.HIGH)        
                
                if ADC0832.getResult() - 60 < 0:
                        res = 0 # laser shining
                else:
                        res = 100 # object passing
                if res > prevRes:
                        # print("object detected")
                        personCounter += 1
                        print("Persons in: ", personCounter)
                        currtime = time.time()
                        if currtime > nexttime:
                                data = json.dumps({'present':personCounter})
                                r = requests.post('https://distributoricarsharing.appspot.com/pi_people',
                                          data = data)
                                nexttime = currtime + 5
                        idletime = 0
                # elif res < prevRes:
                #        pass
                        # print("laser detected")
                else:
                        idletime += 0.2
                        if idletime > 30:
                                personCounter = 0
                                res = 0
                                currtime = time.time()
                                nexttime = currtime + 5
                                idletime = 0
                                print("reset to 0")
                                data = json.dumps({'present':personCounter})
                                r = requests.post('https://distributoricarsharing.appspot.com/pi_people',
                                                  data = data)
                prevRes = res
                
                # print(prevRes, res)
                # print('res = %d' % res)
                time.sleep(0.2)

if __name__ == '__main__':
        init()
        try:
                loop()
        except KeyboardInterrupt:
                GPIO.output(LedPin, GPIO.LOW)     # led off
                ADC0832.destroy()
                print('The end !')


