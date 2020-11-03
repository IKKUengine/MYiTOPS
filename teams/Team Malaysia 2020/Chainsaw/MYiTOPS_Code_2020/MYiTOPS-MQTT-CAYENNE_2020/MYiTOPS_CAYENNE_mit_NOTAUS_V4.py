import pigpio                           #Install every library here in common library path
from enum import Enum
from time import sleep
from time import time
import threading
import cayenne.client

# Servo class with four functions which are the initialization of the function, servo rotation, gas control and switching off the servo respectively.
class Servo:
    def __init__(self, pi, GPIO, Nullposition = 1500, min_Winkel = -20,anschlag_Winkel = 0, max_Winkel = 20):   # Nullpostion gibt die Mittelstellung in Pulsweite an, durch Tests bestimmt
        # example of controlling the direction of servo
        # pi.set_servo_pulsewidth(17, 0)    # off
        # pi.set_servo_pulsewidth(17, 1000) # safe anti-clockwise
        # pi.set_servo_pulsewidth(17, 1500) # centre
        # pi.set_servo_pulsewidth(17, 2000) # safe clockwise
        
        self.GPIO = GPIO
        self.Nullposition = Nullposition
        self.min_Winkel = min_Winkel
        self.anschlag_Winkel = anschlag_Winkel
        self.max_Winkel = max_Winkel
        self.Prozent = 0
        self.Servo_Lib = pi
        
    def move(self, Winkel): # Bewegen mit Winkel, Umrechnung auf Pulsweite
        self.Servo_Lib.set_servo_pulsewidth(self.GPIO, self.Nullposition + (Winkel * 10))
        self.Position = Winkel
        
    def gas_prozent(self, prozent): # Gassteuerung
        self.Prozent = prozent
        self.Position = self.anschlag_Winkel + (prozent*(self.max_Winkel-self.anschlag_Winkel))/100
        self.Servo_Lib.set_servo_pulsewidth(self.GPIO, self.Nullposition + self.Position * 10)
       
    def ausschalten(self): # switching off servo
        self.Servo_Lib.set_servo_pulsewidth(self.GPIO, 0)

# Making classes of different functions for chainsaw engine
# Threading is used to run the processes simultaneously

# Changing the level of choke to coldstart state
class Kaltstart_Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("Kaltstart Thread wird gestartet")
    
    
    def run(self):                 #run function initiates the movement
        global Kaltstart_Flag      #The variables below this is really important for communication
        global Warmstart_Flag      #This script read the status of these variables inside a database
        global Betrieb_Flag        #and defines them here in the script
        global ChangeMode_Flag     #A variable called flag is a python database variable
        
        if Warmstart_Flag:         #If the Warmstart_Flag is equal to 1 in the database, do something
            print("Warmstart eingestellt, umstellen auf Kaltstart")
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Warmstart)
            sleep(0.5)
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_ausfahren)
            sleep(0.5)
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Kaltstart)
            
        elif Betrieb_Flag:         #If the Betrieb_Flag is equal to 1 in the database, do something
            print("Betrieb eingestellt, umstellen auf Kaltstart")
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Betrieb)
            sleep(0.5)
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_ausfahren)
            sleep(0.5)
            Gas_Servo.move(Winkel_Gas_max)
            print("Gas druecken")
            sleep(0.5)
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Kaltstart)
            print("Hebel auf Kaltstart")
            sleep(0.5)
            Gas_Servo.move(Winkel_Gas_min)
            print("Gas auf min")
            
        else:                     #If the choke is at off state, do something
            print("Kaltstart einstellen")
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_aus)
            sleep(0.5)
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_ausfahren)
            print("Hebel ausfahren")
            sleep(0.5)
            Gas_Servo.move(Winkel_Gas_max)
            print("Gas druecken")
            sleep(0.5)
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Kaltstart)
            print("Hebel auf Kaltstart")
            sleep(0.5)
            Gas_Servo.move(Winkel_Gas_min)
            print("Gas auf min")

        sleep(0.5)
        Chokehebel_fahren_Servo.move(Winkel_Chokehebel_einfahren)
        print("Hebel einfahren")
        sleep(0.1)
        print("Kaltstart eingestellt")
        
        Warmstart_Flag = False       #Return or set-up or send the Flags to the database
        Betrieb_Flag = False         #
        Kaltstart_Flag = True        #
        ChangeMode_Flag = False      #
        
        print("Kaltstart Thread wird geschlossen")
        return
            
# Changing the level of choke to warmstart state      
class Warmstart_Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("Warmstart Thread wird gestartet")
        
    def run(self):
        global Kaltstart_Flag   # The same thing happens like class Kaltstart_Thread(threading.Thread):
        global Warmstart_Flag
        global Betrieb_Flag
        global ChangeMode_Flag
        
        if Kaltstart_Flag:
            print("Kaltstart eingestellt, umstellen auf Warmstart")
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Kaltstart)
            sleep(0.5)
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_ausfahren)
            sleep(0.5)
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Warmstart)
        
        elif Betrieb_Flag:
            print("Betrieb eingestellt, umstellen auf Warmstart")
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Betrieb)
            sleep(0.5)
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_ausfahren)
            sleep(0.5)
            Gas_Servo.move(Winkel_Gas_max)
            print("Gas druecken")
            sleep(0.5)
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Kaltstart)
            print("Hebel auf Kaltstart")
            sleep(0.5)
            Gas_Servo.move(Winkel_Gas_min)
            print("Gas auf min")
            sleep(0.5)
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Warmstart)
            print("Hebel auf Warmstart")            
            
        else:
            print("Warmstart einstellen")
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_aus)
            sleep(0.5)
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_ausfahren)
            print("Hebel ausfahren")
            sleep(0.5)
            Gas_Servo.move(Winkel_Gas_max)
            print("Gas druecken")
            sleep(0.5)
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Kaltstart)
            print("Hebel auf Kaltstart")
            sleep(0.5)
            Gas_Servo.move(Winkel_Gas_min)
            print("Gas auf min")
            sleep(0.5)
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Warmstart)
            print("Hebel auf Warmstart")
        
        sleep(0.5)
        Chokehebel_fahren_Servo.move(Winkel_Chokehebel_einfahren)
        print("Hebel einfahren")
        sleep(0.1)
        #Ein wenig zurueckfahren weil Einfahren haengt
#MYiTOPS 2020 check???
        Chokehebel_fahren_Servo.move(Winkel_Chokehebel_einfahren+1)
        print("Warmstart eingestellt")
        
        Kaltstart_Flag = False
        Betrieb_Flag = False
        Warmstart_Flag = True
        ChangeMode_Flag = False
        
        print("Warmstart Thread wird geschlossen")
        return
        
# Changing the level of choke to betrieb state        
class Betrieb_Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("Betrieb Thread wird gestartet")
        
    def run(self):
        global Kaltstart_Flag  # The same thing happens like class Kaltstart_Thread(threading.Thread):
        global Warmstart_Flag
        global Betrieb_Flag
        global ChangeMode_Flag
        
        if Kaltstart_Flag:
            print("Kaltstart eingestellt, umstellen auf Betrieb")
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Kaltstart)
            sleep(0.5)
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_ausfahren)
            sleep(0.5)
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Warmstart)
            sleep(0.5)
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_einfahren)
            print("Hebel einfahren")
            sleep(0.1)
            #Ein wenig zurueckfahren weil Einfahren haengt
#MYiTOPS 2020 check???
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_einfahren+1)
            Gas_Servo.move(Winkel_Gas_max)
            sleep(0.5)
            Gas_Servo.move(Winkel_Gas_min)
            print("Betrieb eingestellt")        
            
        elif Warmstart_Flag:
            print("Warmstart eingestellt, umstellen auf Betrieb")
            Gas_Servo.move(Winkel_Gas_max)
            sleep(0.5)
            Gas_Servo.move(Winkel_Gas_min)
            print("Betrieb eingestellt")
        
        else:
            print("Betrieb einstellen")
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_aus)
            sleep(0.5)
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_ausfahren)
            print("Hebel ausfahren")
            sleep(0.5)
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Betrieb)
            print("Hebel auf Betrieb")
            sleep(0.5)
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_einfahren)
            print("Hebel einfahren")
            sleep(0.1)
            #Ein wenig zurueckfahren weil Einfahren haengt
#MYiTOPS 2020 check???
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_einfahren+1)
            print("Betrieb eingestellt")
     
        Kaltstart_Flag = False
        Warmstart_Flag = False
        Betrieb_Flag = True
        
        ChangeMode_Flag = False
        print("Betrieb Thread wird geschlossen")
        return

# Changing the level of choke to off state
class Motor_stopp_Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("Betrieb Thread wird gestartet")
        
    def run(self):  # The same thing happens like class Kaltstart_Thread(threading.Thread):
        global Motor_an_Flag
        global Kaltstart_Flag
        global Warmstart_Flag
        global Betrieb_Flag
        global ChangeMode_Flag
        
        if Betrieb_Flag:
            Gas_Servo.move(Winkel_Gas_min)
            sleep(0.5)
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Betrieb)
            print("Drehen Betrieb")
            sleep(0.5)
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_ausfahren)
            print("Ausfahren")
            sleep(0.5)
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_aus)
            print("Drehen Aus")
            sleep(0.5)
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_einfahren)
            print("Einfahren")
            
        elif Warmstart_Flag:
            Gas_Servo.move(Winkel_Gas_max)
            sleep(0.5)
            Gas_Servo.move(Winkel_Gas_min)
            sleep(0.5)
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Betrieb)
            print("Drehen Betrieb")
            sleep(0.5)
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_ausfahren)
            print("Ausfahren")
            sleep(0.5)
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_aus)
            print("Drehen Aus")
            sleep(0.5)
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_einfahren)
            print("Einfahren")
            
        elif Kaltstart_Flag:
            Gas_Servo.move(Winkel_Gas_min)
            sleep(0.5)
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Kaltstart)
            print("Drehen Betrieb")
            sleep(0.5)
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_ausfahren)
            print("Ausfahren")
            sleep(0.5)
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_aus)
            print("Drehen Aus")
            sleep(0.5)
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_einfahren)
            print("Einfahren")
            
        Kaltstart_Flag = False
        Warmstart_Flag = False
        Betrieb_Flag = False
        ChangeMode_Flag = False
        print("Motor gestoppt")

class frequence_Thread(threading.Thread):  #This is where we calculate the frequency of the engine
        def __init__(self, pi, gpio, frequencedivider = 1):
            threading.Thread.__init__(self)
            print("Frequenz Thread wird gestartet")
            
            #Declaration of the parameters from the class
            self.pi = pi
            self._tick = 0
            self.frequencelistlength = 10
            self.frequencelist = [0]*self.frequencelistlength
            self.frequencedivider = frequencedivider
            self.frequence = 0
            self.averagefrequence = 0
            self.RPM = 0
            self.Timer = time()
            self.last_tick = 0
            self.pi.set_mode(gpio, pigpio.INPUT)           
            self._cb = self.pi.callback(gpio, pigpio.RISING_EDGE, self._cbf)
            
        def run(self):
            while True:
                self.diff = time()- self.Timer
                if self.last_tick + 0.15 < time():
                    self.frequencelist.insert(0, 0)
                    self.frequencelist.pop()
                sum = 0
                l = self.frequencelist
                for i in range(0,self.frequencelistlength):
                    sum += l[i]
                    
                self.averagefrequence = sum/self.frequencelistlength
                self.RPM = self.averagefrequence*60*self.frequencedivider
                
        def _cbf(self, gpio, level, tick):
            self.last_tick = time()
            t = tick-self._tick
            self.frequence = (1000000.00/t)
            self.frequencelist.insert(0, self.frequence)
            self.frequencelist.pop()
            self._tick = tick
        
        def cancel(self):
            self._cb.cancel()

class Not_Aus_class:                                                # Emergency stop button
    def __init__(self, pi, gpio):
        self.pi = pi
        self.pi.set_mode(gpio, pigpio.INPUT)
        self.pi.set_glitch_filter(gpio, 10000)
        self._cb = self.pi.callback(gpio, pigpio.EITHER_EDGE, self._cbf)
        
    def _cbf(self, gpio, level, tick):
        global Motor_an_Flag
        global Not_Aus_Flag
        global Kaltstart_Flag
        global Warmstart_Flag
        global Betrieb_Flag
        global Gas_Relais_GPIO
        global Chokehebel_fahren_Relais_GPIO
        global Chokehebel_drehen_Relais_GPIO
        #global Zustand
        
        #Not aus betaetigt
        if level == 0:
            Not_Aus_Flag = True
            Motor_an_Flag = False
            print("Notaus betaetigt\n----------------WICHTIG----------------\nVor Loesen des Notaus Chokehebel auf 0 stellen!")
            Gas_Servo.ausschalten()
            Chokehebel_fahren_Servo.ausschalten()
            Chokehebel_drehen_Servo.ausschalten()
            pi.write(Gas_Relais_GPIO, 0)
            pi.write(Chokehebel_fahren_Relais_GPIO, 0)
            pi.write(Chokehebel_drehen_Relais_GPIO, 0)
            LED_off()
            client.virtualWrite(21,1,"digital_sensor" , "d")
            #Zustand = Zustaende.Aus
            Kaltstart_Flag = False
            client.virtualWrite(18,0,"digital_sensor" , "d")
            Warmstart_Flag = False
            client.virtualWrite(19,0,"digital_sensor" , "d")
            Betrieb_Flag = False
            client.virtualWrite(20,0,"digital_sensor" , "d")
                 
        if level == 1:
            sleep(2) #Sichergehen dass die BewegungsThreads geschlossen sind
            client.virtualWrite(21,0,"digital_sensor" , "d")
            Relais_Setup()
            Grundstellung()
            
            Not_Aus_Flag = False
            print("Notaus geloest")    
            
    def cancel(self):
        self._cb.cancel()

def Relais_Setup():
    global Gas_Relais_GPIO
    global Chokehebel_fahren_Relais_GPIO
    global Chokehebel_drehen_Relais_GPIO
        
    pi.write(Gas_Relais_GPIO, 1)
    print("Gas Relais zugeschalten")
    sleep(0.5)
    pi.write(Chokehebel_fahren_Relais_GPIO, 1)
    print("Chokehebel fahren Relais zugeschalten")
    sleep(0.5)
    pi.write(Chokehebel_drehen_Relais_GPIO, 1)
    print("Chokehebel drehen Relais zugeschalten")  
    
# Grundstellung anfahren
def Grundstellung():                                    #Basic Operating mode
    print("Grundstellung wird angefahren")
    sleep(0.5)
    Gas_Servo.move(Winkel_Gas_min)
    Chokehebel_fahren_Servo.move(Winkel_Chokehebel_einfahren)
    sleep(0.2)
    Chokehebel_fahren_Servo.move(Winkel_Chokehebel_einfahren+1) # Rohr haengt, ein bisschen zurueckfahren
    sleep(0.5) # Warten bis Chokehebel eingefahren ist bevor gedreht wird
    Chokehebel_drehen_Servo.move(Winkel_Chokehebel_aus)
    print("Grundstellung angefahren")
    sleep(2)
    
def Test_Profile():
    
    global Time_1
    global Time_2
    global Time_3
    global Throttle_1
    global Throttle_2
    global Throttle_3
    global x
    global y
    global z
    
    if (x<Time_1):
        print('Throttle 1 running')
        Gas_Servo.gas_prozent(Throttle_1)
        # writing to RPM 1 cayenne
        #client.virtualWrite(22, frequence_Reader.RPM, "analog_actuator", "null")
        sleep(1)
        # time increases until it reaches Time 1
        x += 1
        print('Throttle 1 running ')
        
    if (x==Time_1 and y<Time_2):
        Gas_Servo.gas_prozent(Throttle_2)
        # writing to RPM 2 cayenne
        #client.virtualWrite(23, frequence_Reader.RPM, "analog_actuator", "null")
        # time increases until it reaches Time 2
        y += 1
        
    if (x==Time_1 and y==Time_2 and z<Time_3):
        Gas_Servo.gas_prozent(Throttle_3)
        # writing to RPM 3 cayenne
        #client.virtualWrite(24, frequence_Reader.RPM, "analog_actuator", "null")
        # time increases until it reaches Time 3
        z += 1
    
    # Throttle goes back to 0 after test profile is done and time out signal
    if (x==Time_1 and y==Time_2 and z==Time_3):
        Gas_Servo.move(Winkel_Gas_min)
        # writing to Throttle Timeout
        client.virtualWrite(30,1,"digital_sensor" , "d")
    
    
def Motor_start():
    #Led anschalten oder so
    sleep(2)
    
def LED_off():
    global LED_blue_GPIO
    
    # Nullsetzen der LED Ausgnaenge
    pi.write(LED_blue_GPIO, 0)
    
def LED_starting():
    global LED_blue_GPIO
    
    pi.write(LED_blue_GPIO, 1)
    
    
def LED_motor_an():
    global LED_blue_GPIO
 
    pi.write(LED_blue_GPIO, 0)
    
pi = pigpio.pi()    

####################################################################################
####################################################################################

# Pinzuweisung(in GPIO)    # SET GPIO PIN!!! PLEASE CHECK THE ELECTRICAL CONNECTION BEFORE YOU GUYS PROCEED
# Ausgaenge
# PWM
Gas_GPIO = 14
Chokehebel_fahren_GPIO = 15
Chokehebel_drehen_GPIO = 18

#LED
LED_blue_GPIO = 8


# Relais
Gas_Relais_GPIO = 23
Chokehebel_fahren_Relais_GPIO = 24
Chokehebel_drehen_Relais_GPIO = 25

#Eingaenge
Not_Aus_GPIO = 17
Frequenz_GPIO = 20 #normal 27, umgesteckt fuer Q1 Ausgang

#####################################################################################
#####################################################################################


# Angefahrene Winkel der Servos deklarieren, bei Werkzeugwechsel anpassen

Winkel_Chokehebel_einfahren = 5
Winkel_Chokehebel_ausfahren = 35
Winkel_Chokehebel_aus = 75
Winkel_Chokehebel_Betrieb = 42
Winkel_Chokehebel_Warmstart = 14
Winkel_Chokehebel_Kaltstart = -8
Winkel_Gas_min = -40
Winkel_Gas_Anschlag = -19
Winkel_Gas_max = -8

# Servos deklarieren (Pin, Nullstellung, min Winkel, max Winkel)

Gas_Servo = Servo(pi, Gas_GPIO,1500, Winkel_Gas_min, Winkel_Gas_Anschlag, Winkel_Gas_max)
Chokehebel_fahren_Servo = Servo(pi, Chokehebel_fahren_GPIO, 1500)
Chokehebel_drehen_Servo = Servo(pi, Chokehebel_drehen_GPIO, 1500)

# Frequenz Thread definieren

frequence_Reader = frequence_Thread(pi, Frequenz_GPIO, 2)

# Not Aus Klasse deklarieren

Not_Aus = Not_Aus_class(pi, Not_Aus_GPIO)

pi.set_mode(Gas_Relais_GPIO, pigpio.OUTPUT)
pi.set_mode(Chokehebel_fahren_Relais_GPIO, pigpio.OUTPUT)
pi.set_mode(Chokehebel_drehen_Relais_GPIO, pigpio.OUTPUT)
# Pull Down der Relaisausgaenge
pi.set_pull_up_down(Gas_Relais_GPIO, pigpio.PUD_DOWN)
pi.set_pull_up_down(Chokehebel_fahren_Relais_GPIO, pigpio.PUD_DOWN)
pi.set_pull_up_down(Chokehebel_drehen_Relais_GPIO, pigpio.PUD_DOWN)

#Nullsetzen der Relaisausgaenge
pi.write(Gas_Relais_GPIO, 0)
pi.write(Chokehebel_fahren_Relais_GPIO, 0)
pi.write(Chokehebel_drehen_Relais_GPIO, 0)


Kaltstart_Flag = False                     #### THESE VARIABLES ARE REALLY IMPORTANT, SET ALL VARIABLES INTO FALSE OR 0 FIRST
Warmstart_Flag = False                     #### AND THEN THE SCRIPT WILL UPDATE THE INFORMATION OF THESE VARIABLES AFTER CONNECTED TO THE DATABASE
Betrieb_Flag = False
ChangeMode_Flag = False
Motor_an_Flag = False
Not_Aus_Flag = False

FreischneideButton_Flag = False
TrennschleiferButton_Flag = False
MotorSaegeButton_Flag = False

KaltstartButton_Flag = False
WarmstartButton_Flag = False
BetriebButton_Flag = False

OnOff_Flag = False
StartStopSignalButton_Flag = False
TestProfileButton_Flag = False

Connection_Counter = 0
Counter = 0

#Test Profile
Time_1 = 0
Time_2 = 0
Time_3 = 0
Throttle_1 = 0
Throttle_2 = 0
Throttle_3 = 0
Throttle = 0

# Zeit
Motor_Timer = time()
Connection_Timer = 0

# Comparator
x = 1
y = 1
z = 1

MQTT_USERNAME  = "67b20550-7b33-11ea-883c-638d8ce4c23d"
MQTT_PASSWORD  = "dd7e85f7ef61ffc87e068d1634463cd59ddb7cfa"
MQTT_CLIENT_ID = "346f3e40-8341-11ea-a67f-15e30d90bbf4"

client = cayenne.client.CayenneMQTTClient()
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID)

client.virtualWrite(8,0)

def on_message(message):
    global OnOff_Flag
    global MotorSaegeButton_Flag
    global FreischneideButton_Flag
    global TrennschleiferButton_Flag
    global KaltstartButton_Flag
    global WarmstartButton_Flag
    global BetriebButton_Flag
    global StartStopSignalButton_Flag
    global TestProfileButton_Flag
    global Time_1
    global Time_2
    global Time_3
    global Throttle_1
    global Throttle_2
    global Throttle_3
    global Throttle
    
    if message.channel==1 :    #channel for on/off button
        if message.value=="1": 
            OnOff_Flag = True
        elif message.value=="0":
            OnOff_Flag = False
    
    elif message.channel==2 :  #channel for MS 
        if message.value=="1": 
            MotorSaegeButton_Flag = True
        elif message.value=="0":
            MotorSaegeButton_Flag = False
            
    elif message.channel==3 :  #channel for FS 
        if message.value=="1": 
            FreischneideButton_Flag = True
        elif message.value=="0":
            FreischneideButton_Flag = False
            
    elif message.channel==4 :  #channel for TS 
        if message.value=="1": 
            TrennschleiferButton_Flag = True
        elif message.value=="0":
            TrennschleiferButton_Flag = False
            
    elif message.channel==5:   #channel for cold start button   
        if message.value=="1": 
            KaltstartButton_Flag = True
        elif message.value=="0":
            KaltstartButton_Flag = False
            client.virtualWrite(18,0,"digital_sensor" , "d")
            
    elif message.channel==6:    #channel for warm start button 
        if message.value=="1": 
            WarmstartButton_Flag = True
        elif message.value=="0":
            WarmstartButton_Flag = False
            client.virtualWrite(19,0,"digital_sensor" , "d")
            
    elif message.channel==7:    #channel for betrieb button
        if message.value=="1": 
            BetriebButton_Flag = True
        elif message.value=="0":
            BetriebButton_Flag = False
            client.virtualWrite(20,0,"digital_sensor" , "d")
            
    elif message.channel==8 :    #channel for start/stop engine button
        if message.value=="1": 
            StartStopSignalButton_Flag = True
        elif message.value=="0":
            StartStopSignalButton_Flag = False
            
    elif message.channel==9 :  #channel for on/off test profile button
        if message.value=="1": 
            TestProfileButton_Flag = True
        elif message.value=="0":
            TestProfileButton_Flag = False
            
    elif message.channel==11 :  #channel for throttle 1 slider
        Throttle_1 = float(message.value)
        
    elif message.channel==12 :  #channel for throttle 2 slider
        Throttle_2 = float(message.value)
        
    elif message.channel==13 :  #channel for throttle 3 slider
        Throttle_3 = float(message.value)
        
    elif message.channel==14 :  #channel for time 1 slider
        Time_1 = float(message.value)
        
    elif message.channel==15 :  #channel for time 2 slider
        Time_2 = float(message.value)
        
    elif message.channel==16 :  #channel for time 3 slider
        Time_3 = float(message.value)
    
    elif message.channel==17 :  #channel for throttle
        Throttle = float(message.value)
        

if __name__ == "__main__":
    Relais_Setup()
    Grundstellung()

    try:
        while True:
            client.loop()
            client.on_message = on_message
                
            if OnOff_Flag:
                if MotorSaegeButton_Flag:
                    if not ChangeMode_Flag and KaltstartButton_Flag and not WarmstartButton_Flag and not BetriebButton_Flag and not Kaltstart_Flag and not StartStopSignalButton_Flag and not Not_Aus_Flag and not Motor_an_Flag:
                        ChangeMode_Flag = True
                        Kaltstart = Kaltstart_Thread()
                        Kaltstart.start()
                        client.virtualWrite(18,1,"digital_sensor" , "d")
                        
                    elif not ChangeMode_Flag and WarmstartButton_Flag and not KaltstartButton_Flag and not BetriebButton_Flag and not Warmstart_Flag and not StartStopSignalButton_Flag and not Not_Aus_Flag and not Motor_an_Flag:
                        ChangeMode_Flag = True
                        Warmstart = Warmstart_Thread()
                        Warmstart.start()
                        client.virtualWrite(19,1,"digital_sensor" , "d")
                        #Zustand = Zustaende.Warmstart

                    elif not ChangeMode_Flag and BetriebButton_Flag and not KaltstartButton_Flag and not WarmstartButton_Flag and not Betrieb_Flag and not StartStopSignalButton_Flag and not Not_Aus_Flag and not Motor_an_Flag:
                        print("3 ",ChangeMode_Flag)
                        ChangeMode_Flag = True
                        Betrieb = Betrieb_Thread()
                        Betrieb.start()
                        client.virtualWrite(20,1,"digital_sensor" , "d")
                        #Zustand = Zustaende.Betrieb
                
                # Motor starten
                if (Kaltstart_Flag or Warmstart_Flag or Betrieb_Flag) and StartStopSignalButton_Flag and not Motor_an_Flag and not Not_Aus_Flag and not ChangeMode_Flag:
                    if Counter == 0:
                         LED_starting()
            
                    if Motor_Timer + 10 < time():
                        LED_off()
                        if frequence_Reader.RPM > 1500:
                            print("Motor an erkannt")
                            Motor_an_Flag = True
                            LED_motor_an()
                            if Warmstart_Flag or Kaltstart_Flag:
                                Betrieb = Betrieb_Thread()
                                Betrieb.start()
                                client.virtualWrite(20,1,"digital_sensor" , "d")
                                #Zustand = Zustaende.Betrieb
                            continue
                        
                        # Bei 5 Startversuchen in Warm oder Kaltstart auf Betrieb umschalten 
                        if Counter == 5 and (Kaltstart_Flag or Warmstart_Flag) and StartStopSignalButton_Flag and not Motor_an_Flag and not Not_Aus_Flag and not ChangeMode_Flag:
                            ChangeMode_Flag = True
                            print("Fuenf Startversuche in Warm/Kaltstart, umstellen auf Betrieb")
                            Betrieb = Betrieb_Thread()
                            Betrieb.start()
                            client.virtualWrite(20,1,"digital_sensor" , "d")
                            #Zustand = Zustaende.Betrieb
                            continue
                    
                    if Motor_Timer + 15 < time():
                        LED_starting()
                        Counter += 1
                        Motor_Timer = time()
                        print("Motor Start\n Anzahl Startversuche: {}".format(Counter))
                        
                elif not StartStopSignalButton_Flag:
                    Counter = 0
                    
                # Testing for throttle position without engine start
                if (not Kaltstart_Flag and not Warmstart_Flag and not Betrieb_Flag) and not Motor_an_Flag and Gas_Servo.Prozent != Throttle and not Not_Aus_Flag:
                   print("aktuelles Gas zum Test in Prozent: ", Throttle)
                   Gas_Servo.gas_prozent(Throttle)
                
                # Cayenne Test Profile    
                if MotorSaegeButton_Flag and (Kaltstart_Flag or Warmstart_Flag or Betrieb_Flag) and not Not_Aus_Flag and TestProfileButton_Flag and Throttle == 0:
                    Test_Profile()
                
                # Motor ausschalten
                if Motor_an_Flag and (not StartStopSignalButton_Flag or frequence_Reader.RPM == 0) and not Not_Aus_Flag:
                    print("Motor war an, ausstellen")
                    ChangeMode_Flag = True
                    Motor_an_Flag = False
                    LED_off()
                    Counter = 0
                    Motor_stopp = Motor_stopp_Thread()
                    Motor_stopp.start()
                    #Zustand = Zustaende.Aus
            
                
    except KeyboardInterrupt:
        print("Anlage aus")
        Gas_Servo.ausschalten()
        Chokehebel_fahren_Servo.ausschalten()
        Chokehebel_drehen_Servo.ausschalten()
        pi.write(Gas_Relais_GPIO, 0)
        pi.write(Chokehebel_fahren_Relais_GPIO, 0)
        pi.write(Chokehebel_drehen_Relais_GPIO, 0)
        pi.stop()
        Not_Aus.cancel()

