"""
KY040 Code form Martin O'Hanlon and Conrad Storz 
stuffaboutcode.com

ULN2003A Code of stepper from Ingmar Stapel
https://github.com/custom-build-robots/Stepper-motor-28BYJ-48-Raspberry-Pi/blob/master/decision-maker.py

MYiTOPS Code by Ferhat Aslan (University of Applied Science)
"""
'''
Please enter the IP address of the server and the name of the client here. Change the transfer rate if desired.
'''

ClIENTNAME = "MYiTOPS Client V2"
ipAdress = '192.168.178.24'
# value in seconds
TRANSFERRATE = 0.5#0.2
# Waiting time for the speed of stepper motor
STEPPERTIME = 0.001

#GBIO Pins 
CLOCKPIN = 27
DATAPIN = 22
SWITCHPIN = 17
PUSHBUTTON1 = 5
PUSHBUTTON2 = 6
LED1 = 12        #Green
LED2 = 25        #Red

# Used pins of the ULN2003A
IN1=13 # IN1
IN2=24 # IN2
IN3=18 # IN3
IN4=23 # IN4

import RPi.GPIO as GPIO
import socket
from PySide import QtNetwork, QtCore, QtGui
import time
import threading
import re

GPIO.setmode(GPIO.BCM)

class Stopping:
    def __init__(self, rider, once):
        self.rider = rider
        self.once = once
    def getRider(self):
        return self.rider
    def setRider(self, bool):
        self.rider = bool
    def getOnce(self):
        return self.once
    def setOnce(self, bool):
        self.once = bool

class MYiTOPS:

    CLOCKWISE = 0
    ANTICLOCKWISE = 1
    DEBOUNCE = 60

    def __init__(self, clockPin, dataPin, switchPin, pushbutton1Pin, pushbutton2Pin,
                 led1Pin, led2Pin, in1, in2, in3, in4, rotaryCallback, switchCallback,
                 pushbutton1Callback, pushbutton2Callback):    
        #persist values
        self.clockPin = clockPin
        self.dataPin = dataPin
        self.switchPin = switchPin
        self.rotaryCallback = rotaryCallback
        self.switchCallback = switchCallback
        self.pushbutton1Pin = pushbutton1Pin
        self.pushbutton2Pin = pushbutton2Pin
        self.led1Pin = led1Pin
        self.led2Pin = led2Pin
        self.in1 = in1
        self.in2 = in2
        self.in3 = in3
        self.in4 = in4
        self.pushbutton1Callback = pushbutton1Callback
        self.pushbutton2Callback = pushbutton2Callback
        self.volume = 0
        self.runningMotor = 0
        self.push1 = False
        self.push2 = False
        self.dirMotor = False
        self.stepperSteps = 0
        self.motorDrive = False

        self.loop = True

        #setup pins
        GPIO.setup(clockPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(dataPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(switchPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.setup(pushbutton1Pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(pushbutton2Pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        GPIO.setup(led1Pin, GPIO.OUT)
        GPIO.setup(led2Pin, GPIO.OUT)
        
        GPIO.setup(in1,GPIO.OUT)
        GPIO.setup(in2,GPIO.OUT)
        GPIO.setup(in3,GPIO.OUT)
        GPIO.setup(in4,GPIO.OUT)
    #----------------------Stepper Begin----------------------------
    
    # The 28BYJ-48 stepper motor is designed so that the motor is
    # Inside 8 steps needed for one turn. Through the operations
    # but it takes 512 x 8 steps for the axis to rotate once
    # So turns itself 360°

    # Definition of steps 1 - 8 via pins IN1 to IN4
    # Between each movement of the motor is waited for a short time so that the
    # Motor anchor reaching its position.
    
    def Step1(self):
        GPIO.output(IN4, True)
        time.sleep(STEPPERTIME)
        GPIO.output(IN4, False)

    def Step2(self):
        GPIO.output(IN4, True)
        GPIO.output(IN3, True)
        time.sleep(STEPPERTIME)
        GPIO.output(IN4, False)
        GPIO.output(IN3, False)

    def Step3(self):
        GPIO.output(IN3, True)
        time.sleep(STEPPERTIME)
        GPIO.output(IN3, False)

    def Step4(self):
        GPIO.output(IN2, True)
        GPIO.output(IN3, True)
        time.sleep(STEPPERTIME)
        GPIO.output(IN2, False)
        GPIO.output(IN3, False)

    def Step5(self):
        GPIO.output(IN2, True)
        time.sleep(STEPPERTIME)
        GPIO.output(IN2, False)

    def Step6(self):
        GPIO.output(IN1, True)
        GPIO.output(IN2, True)
        time.sleep(STEPPERTIME)
        GPIO.output(IN1, False)
        GPIO.output(IN2, False)

    def Step7(self):
        GPIO.output(IN1, True)
        time.sleep(STEPPERTIME)
        GPIO.output(IN1, False)

    def Step8(self):
        GPIO.output(IN4, True)
        GPIO.output(IN1, True)
        time.sleep(STEPPERTIME)
        GPIO.output(IN4, False)
        GPIO.output(IN1, False)
 
    def left(self, steps):
        for i in range (steps): 
            self.Step1()
            self.Step2()
            self.Step3()
            self.Step4()
            self.Step5()
            self.Step6()
            self.Step7()
            self.Step8()
        print ("Steps left: ", steps) 
       
    def right(self, steps):
        for i in range (steps):  
            self.Step8()
            self.Step7()
            self.Step6()
            self.Step5()
            self.Step4()
            self.Step3()
            self.Step2()
            self.Step1()  
        print ("Steps right: ", steps) 
        
    #--------------------Stepper End--------------------------------
    
    def getValues(self):
        return str(self.runningMotor) + ", '"+ str(self.push1)+ "', '" + str(self.push2) + "', "+ str(self.volume)

    def start(self):
        GPIO.add_event_detect(self.clockPin, GPIO.FALLING, callback=self._clockCallback, bouncetime=self.DEBOUNCE)
        GPIO.add_event_detect(self.switchPin, GPIO.FALLING, callback=self._switchCallback, bouncetime=self.DEBOUNCE)    
        GPIO.add_event_detect(self.pushbutton1Pin, GPIO.FALLING, callback=self._pushbutton1Callback, bouncetime=self.DEBOUNCE)
        GPIO.add_event_detect(self.pushbutton2Pin, GPIO.FALLING, callback=self._pushbutton2Callback, bouncetime=self.DEBOUNCE)

    def stop(self):
        GPIO.remove_event_detect(self.clockPin)
        GPIO.remove_event_detect(self.switchPin)
        GPIO.remove_event_detect(self.pushbutton1Pin)
        GPIO.remove_event_detect(self.pushbutton2Pin)
        
    
    def _clockCallback(self, pin):
        if GPIO.input(self.clockPin) == 0:
            #self.rotaryCallback(GPIO.input(self.dataPin))
        
            data = GPIO.input(self.dataPin)
            if data == 0 and self.volume < 20:
                self.volume += 1
            elif data == 1 and self.volume > 0:
                self.volume -= 1
        print (self.volume)
    
    def _switchCallback(self, pin):
        self.volume = 0
        print ("Volume is set to zero.")
        print (self.volume)
        #self.switchCallback(pin)
        
    def getStepperSteps(self, steps):
        #self.stepsStepper = GPIO.input(self.laverSwitchPin)
        return self.stepsStepper
 
        
    def _pushbutton1Callback(self, pin):
        self.push1 = not self.push1
        print(self.push1)

    def _pushbutton2Callback(self, pin):
        #self.pushbutton2Callback(pin)
        self.push2 = not self.push2
        print(self.push2)
        
    def setLed1(self, on):
        if on: 
            GPIO.output(self.led1Pin, GPIO.HIGH)
        else:
            GPIO.output(self.led1Pin, GPIO.LOW)
            
    def setLed2(self, on):
        if on: 
            GPIO.output(self.led2Pin, GPIO.HIGH)
        else:
            GPIO.output(self.led2Pin, GPIO.LOW)
         
    def setDriveMotor(self, on):
        if on: 
            self.motorDrive = True
        else:
            self.motorDrive = False
    
    def getDriveMotor(self):
        return self.motorDrive
    
    def setStepperSteps(self, steps):
        self.stepperSteps = steps
        
    def setRunningMotor(self, on):
        self.runningMotor = on
        
    def getStepperSteps(self):
        return self.stepperSteps 
        
    def setDirecionMotor(self, dir):
        if dir == 0: 
            self.dirMotor = True
        else:
            self.dirMotor = False

    def getDirecionMotor(self):
        return self.dirMotor
        
    def setStoppAppClient(self, on):
        if on: 
            self.setExit()
        else:
            pass
        
    def setExit(self):
        print("exit")
        self.loop = False
        
    def getExit(self):
        #print (self.loop)
        return self.loop

if __name__ == "__main__":
    
    byteMessageList = []
    values = "0, 0, 0, 0, 0"

    print ('Program start.')

    def rotaryChange(direction):
        print ("turned - " + str(direction))
    def switchPressed(pin):
        print ("button connected to pin:{} pressed".format(pin))
        
    def pushbutton1(pin):
        MYiTOPS.setExit()
        
    def pushbutton2(pin):
        print ("button connected to pin:{} pressed".format(pin))
   
    def comToServer(values):
        try:
            on = '1'
            off = '0'      
            header = "'{}' ('Steps Stepper', 'Push Button 1', 'Push Button 2', 'Encoder Volume') VALUES ".format(ClIENTNAME)
            message = "{} ({})".format(header, values)
            #message = "E5"
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10.0)
            s.connect((ipAdress, 50005))
            #print ("Connection etaNet is done")
            block = QtCore.QByteArray()
            out = QtCore.QDataStream(block, QtCore.QIODevice.WriteOnly)
            out.setVersion(QtCore.QDataStream.Qt_4_0)                                
            #print(message)                    
            out.writeQString(message)             
            s.send(block.data())
            
            block2 = QtCore.QByteArray()
            into = QtCore.QDataStream(block2, QtCore.QIODevice.ReadWrite)
            into.setVersion(QtCore.QDataStream.Qt_4_0)
            message = s.recv(1024)
            
            s.close()
            return message
        except:
            print ("NO Connection to etaNet. Please check your connection to server!")
    
    def networkThread():
        while MYiTOPS.getExit(): 
            try:
                byteMessageList = []
                strMessageList = []
                newList = []
                data = comToServer(MYiTOPS.getValues())
                #print (data)

                byteMessageList = list(data.decode('ascii'))
                strMessage = ''.join(str(x) for x in byteMessageList)
                strMessageList = strMessage.split(";")
                for i in strMessageList:
                   newList.append( str(i.split(chr(0))).replace(' ', '').replace(',', '').replace(']', '').replace('[', '').replace("'", ''))
                newList[0] = str(re.findall(r'\d+\.*\d*', newList[0])).replace("'", '').replace(']', '').replace('[', '')
                
                if newList[0] == ('04, 5'):
                    #print("E5")
                    pass

                elif len(newList)== 6:
                    MYiTOPS.setStepperSteps(int(newList[0]))
                    MYiTOPS.setLed1(int(newList[1]))
                    MYiTOPS.setLed2(int(newList[2]))
                    MYiTOPS.setDriveMotor(int(newList[3]))
                    MYiTOPS.setDirecionMotor(int(newList[4]))
                    MYiTOPS.setStoppAppClient(int(newList[5]))
                
                else:
                    print("Wrong message! Please check your conection.")
            except:
                print ("Communication via the network could not be started.")
                MYiTOPS.setExit()
                
    def motorThread():
        while MYiTOPS.getExit()          
            try:
                time.sleep(0.2)
                if MYiTOPS.getDriveMotor() == False:
                    pass
                    
                else:
                    MYiTOPS.setRunningMotor(1)
                    if MYiTOPS.getDirecionMotor() == True:
                        MYiTOPS.left(MYiTOPS.getStepperSteps())
                    else:
                        MYiTOPS.right(MYiTOPS.getStepperSteps())
                    MYiTOPS.setRunningMotor(0)

            except:
                print ("Stepper Motor could not be started.")
                MYiTOPS.setExit()
        
MYiTOPS = MYiTOPS(CLOCKPIN, DATAPIN, SWITCHPIN, PUSHBUTTON1, PUSHBUTTON2, LED1, LED2,
                  IN1, IN2, IN3, IN4, rotaryChange, switchPressed, pushbutton1, pushbutton2)
 
 
print ('MYiTOPS Remote Control Client.')

MYiTOPS.start()

try:
    MYiTOPS.setLed1(True)
    MYiTOPS.setLed2(True)
    time.sleep(0.3)
    MYiTOPS.setLed1(False)
    MYiTOPS.setLed2(True)
    time.sleep(0.3)
    MYiTOPS.setLed2(False)
    MYiTOPS.setLed1(True)
    time.sleep(0.3)
    MYiTOPS.setLed1(True)
    MYiTOPS.setLed2(True)
    time.sleep(0.3)
    MYiTOPS.setLed1(False)
    MYiTOPS.setLed2(False)

    #Starting Client Threads
    
    sending = threading.Thread(target = networkThread)
    motorRun = threading.Thread(target = motorThread)
    motorRun.start()
    sending.start()
    sending.join()
    motorRun.join()

except:
    print ("Error: unable to start client")
    
finally:
    MYiTOPS.stop()
    GPIO.cleanup()
