## Creates functions for connecting to and controlling arduino motion

import serial
from time import sleep
import time

def in_range(val, start, end):
    # determine the input value is in the supplied range
    return (val >= start and val <= end)

class Launcher:
    def __init__(self, serPort = '/dev/ttyUSB0', baud = 9600):
        self.serPort = serPort
        self.baud = baud
        self.ser = None #Serial object for connection
        
    def connect(self):
        self.ser = serial.Serial(self.serPort, baudrate=self.baud)
        print(self.ser.read_until()) #waiting for startup message
        
    def disconnect(self):
        self.ser.close()
        
    def pan(self,angle):
        '''
        Input angle (in degrees as int/float) and launcher will pan to that angle.
        Note that 0 pan angle is defined by the position of the stepper motor when power is connected
        '''
        command = 'pan'+str(angle) + '\r'
        self.ser.write(command.encode('utf8'))
        self.ser.read_until(b'p\r\n') #look for confirmation message sent from arduino

    def tilt(self,angle):
        '''
        Input angle (in degrees as int/float) and launcher will tilt to that angle.
        Note that 0 tilt angle is set internally by the servo and is always the same.
        Range of tilt angles is dependent on servo but should generally be between [80,140]
        to avoid collision of the camera/loader arm and the servo.
        '''
        command = 'tilt'+str(angle) + '\r'
        self.ser.write(command.encode('utf8'))
        self.ser.read_until(b't\r\n') #look for confirmation message sent from arduino

    def motor(self, val):
        '''
        Turns motor on (val=1) or off (val=0)
        '''
        command = 'motor'+str(val) + '\r'
        self.ser.write(command.encode('utf8'))
        self.ser.read_until(b'm\r\n') #look for confirmation message sent from arduino
            
    def load(self):
        '''
        When called, loads a ball into the launcher
        '''
        self.ser.write(('load\r').encode('utf8'))
        self.ser.read_until(b'l\r\n') #look for confirmation message sent from arduino

#Test script
'''
myLauncher = Launcher()
myLauncher.connect()
myLauncher.pan(10)
myLauncher.pan(-10)
myLauncher.tilt(80)
myLauncher.tilt(110)
myLauncher.motor(1)
sleep(2)
myLauncher.load()
myLauncher.motor(0)
myLauncher.disconnect()
'''

class PID: #Inspired from https://www.pyimagesearch.com/2019/04/01/pan-tilt-face-tracking-with-a-raspberry-pi-and-opencv/
    def __init__(self, kP=1, kI=0, kD=0):
        #initialise gains
        self.kP = kP
        self.kI = kI
        self.kD = kD
        
    def initialise(self):
        #initialise the current and previous time
        self.currTime = time.time()
        self.prevTime = self.currTime
        
        #initialise the previous error
        self.prevError = 0
        
        #initialise the term result variables
        self.cP = 0
        self.cI = 0
        self.cD = 0
    
    def update(self, error, sleep=0):
        #pause for a bit
        time.sleep(sleep)
        
        #grab the current time and calculate dt
        self.currTime = time.time()
        dt = self.currTime - self.prevTime
        
        #dErr
        dErr = error - self.prevError
        
        #Calculate PID terms
        self.cP = error
        self.cI += error*dt
        self.cD = (dErr/dt) if dt > 0 else 0
        
        #save previous time and error for the next update
        self.prevTime = self.currTime
        self.prevError = error
        
        #Sum the terms and return
        return sum([self.kP*self.cP, self.kI*self.cI, self.kD*self.cD]) 