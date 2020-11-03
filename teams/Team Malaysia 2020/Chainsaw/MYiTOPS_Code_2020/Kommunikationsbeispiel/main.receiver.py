#!python3

######################################################################################################
# Adapted by Danial Haris Limi Hawari, LiDa17, dannyalharris@gmail.com                               #
# MQTT Energy Management System for IKKU Lab 043, Hochschule Karlsruhe, HsKA                         #
######################################################################################################

import paho.mqtt.client as mqtt #install the library using "sudo pip3 install paho-mqtt"
import json
import datetime
import time
import random
import logging
import threading
from threading import Thread


client_is_sender = False
mqttclient_log=False #MQTT client logs showing messages
logging.basicConfig(level=logging.INFO) #Error logging
settings=dict()
subscriber_dict=dict()
publisher_dict=dict()

# quality of service --> publish-feature
qosAtMostOnce = 0
qosAtLeastOnce = 1
qosExactlyOnce = 2

#### User should edit this field
brokers = ["localhost", "192.168.178.20",
           "test.mosquitto.org", "broker.hivemq.com", 
           "iot.eclipse.org", "mqtt.eclipse.org"] # Public open broker to test
# Set MQTT broker IP adress, whether VerneMQ broker or public online broker

settings["broker"]=brokers[3] # Stored array in dictionary. brokers[0]= "localhost"
settings["username"]="IKKULab043" # MQTT broker username, VerneMQ broker username in our case
settings["password"]="IKKULab000" # MQTT broker password, VerneMQ broker password in our case
settings["port"]=1883 # MQTT broker port
settings["clientname"]="MQTT-EMS-MYITOPS" # Set client name or this instance name

topicMYITOPS = "HsKA/IKKULab/IKKULab043/CPS/MYITOPS"
settings["topics"]=[(topicMYITOPS, 2)]

#settings["topics"]=[("HsKA/IKKULab/IKKULab043/CPS/#",0),("HsKA/IKKULab/IKKULab043/CPS/CHP",0),
#                    ("HsKA/IKKULab/IKKULab043/CPS/Buffer/Monitoring/Sensor/TempSensor/Temperature",1),
#                    ("HsKA/IKKULab/IKKULab043/CPS/Consumer/Controlling/Actuator/HeatElement/Parameter",2),
#                    ("HsKA/IKKULab/IKKULab043/CPS/ECar/Monitoring/#",1)]
# settings["topics"]=[("HsKA/#",2)]
# settings["topics"]=[("HsKA/IKKULab/IKKULab043/CPS/+/Monitoring/#",2)]
# settings["topics"]=[("anything/anything/anything",1)]

# Set topics that we would like to subscribe together with their QoS level, 0, 1, 2.
# You can use '#' or '+' as a wildcard to subscribe multilevel topics or all topics at the same level
# topics at the same time
####

#### Publish to topic
# Do something inside the publishing_message() as example
def publishing_message():
    time.sleep(10)
    timestampStr = str(datetime.datetime.now())

    r1 = str(random.randrange(1, 10000))
    r2 = str(random.randrange(1, 10000))
    r3 = str(random.randrange(1, 10000))
    r4 = str(random.randrange(1, 100))
    r5 = str(random.randrange(1, 100))

    # Change the value inside here
    publisher_dict = {"Publisher": "R.Pi-MYITOPS",
                      "SystemType": "Monitoring-"+ r1, "Purpose": "Frequency",
                      "ParameterValue": r2 , "Remark": "Other value: "+ r3 }

    publisher_json = json.dumps(publisher_dict)
    print(publisher_json)

    client.publish(topicMYITOPS, publisher_json, qos=qosExactlyOnce)
####


def on_connect(client, userdata, flags, rc):
   logging.debug("Connected flags" + str(flags) + "result code " \
                 + str(rc) + "client1_id")
   if rc == 0:
      client.connected_flag = True
      print("Connected to broker: " + settings["broker"])
   else:
      client.bad_connection_flag = True


def on_disconnect(client, userdata, rc):
   logging.debug("disconnecting reason " + str(rc))
   client.connected_flag = False
   client.disconnect_flag = True
   client.subscribe_flag = False


def on_subscribe(client, userdata, mid, granted_qos):
   m = "in on subscribe callback result " + str(mid)
   logging.debug(m)
   client.subscribed_flag = True

#### Subcribing message
def on_message(client, userdata, message):
   #Do something with the subscribed message here
   timestampStr = str(datetime.datetime.now())
   subscriber_dict = json.loads(str(message.payload.decode("utf-8", "ignore")))  # Convert json message
#   subscriber_dict["Topic"] = message.topic  # into python dict
#   subscriber_dict["Timestamp"] = timestampStr
   print("received message:")
   print (subscriber_dict)

def on_log(client, userdata, level, buf):
   print(userdata)

def Initialise_clients(clientname, cleansession=True):
   # flags set
   client = mqtt.Client(clientname)
   client.connected_flag=False #  flag for connection
   client.bad_connection_flag=False
   client.subscribed_flag=False
   if mqttclient_log:  # enable mqqt client logging
      client.on_log = on_log
      
   # callbacks
   client.on_connect = on_connect  # attach function to callback
   if not client_is_sender:
      client.on_message = on_message  # attach function to callback
   client.on_disconnect = on_disconnect
   client.on_subscribe = on_subscribe
   
   return client

def convert(t):
    d=""
    for c in t:  # replace all chars outside BMP with a !
            d =d+(c if ord(c) < 0x10000 else '!')
    return(d)

####

#### Main program

if not settings["clientname"]:
    r=random.randrange(1,10000)
    clientname="IKKULabEMS-"+str(r)
else:
    clientname="IKKULabEMS-"+str(settings["clientname"])

#### Initialise_client_object() #  add extra flags

logging.info(" creating client "+clientname)
client=Initialise_clients(clientname,False) # create and initialise client object

if settings["username"] !="":
    print("setting broker's username:",settings["username"],"and password:",settings["password"])
    client.username_pw_set(settings["username"], settings["password"])

client.connect(settings["broker"],settings["port"])
# client.connect(settings["broker"], settings["port"], settings["keepalive"]))
client.loop_start()

while not client.connected_flag: # wait for connection
    print("waiting for connection")
    time.sleep(1)

client.subscribe(settings["topics"])

while not client.subscribed_flag: # wait to subscribe to topic
    print("waiting for subscribe")
    time.sleep(1)

print("subscribed topic:",settings["topics"])


#### loop and wait until interrupted
try:
    while True:
       if client_is_sender:
          publishing_message()
       else:
          pass
       
except KeyboardInterrupt:
    print("interrrupted by keyboard")

####

client.loop_stop()  # final check for messages
time.sleep(5)

print("program stop")


#The program is still not finished to integrate with MQTT system 15/02/2020
"""
#!/usr/bin/python

""
MYiTOPSGermany
Python Subteam
Autoren : Danial Haris Bin Limi Hawari, Fabian Harlacher

Script zur Steuerung der Aktorik der Hoehen- und Klimakammer des IKKU in Bruchsal per Datenbank


""

import pigpio
from enum import Enum
from time import sleep
from time import time
import mysql.connector
from mysql.connector import errorcode
import threading


    
# Klasse Sevo zum einbinden von pigpio und Fahren mit integrierter Winkel zu Pulsweiteumrechnung / Gassteuerung
class Servo:
    def __init__(self, pi, GPIO, Nullposition = 1500, min_Winkel = -20,anschlag_Winkel = 0, max_Winkel = 20):   # Nullpostion gibt die Mittelstellung in Pulsweite an, durch Tests bestimmt
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
       
    def ausschalten(self):
        self.Servo_Lib.set_servo_pulsewidth(self.GPIO, 0)
       
class Kaltstart_Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("Kaltstart Thread wird gestartet")
        
    def run(self):
        global Kaltstart_Flag
        global Warmstart_Flag
        global Betrieb_Flag
        global ChangeMode_Flag
        
        if Warmstart_Flag:
            print("Warmstart eingestellt, umstellen auf Kaltstart")
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Warmstart)
            sleep(0.5)
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_ausfahren)
            sleep(0.5)
            Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Kaltstart)
        elif Betrieb_Flag:
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
            
        else:
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
        #Ein wenig zurueckfahren weil Einfahren haengt
        Chokehebel_fahren_Servo.move(Winkel_Chokehebel_einfahren+1)
        print("Kaltstart eingestellt")
        
        Warmstart_Flag = False
        Betrieb_Flag = False
        Kaltstart_Flag = True
        ChangeMode_Flag = False
        
        print("Kaltstart Thread wird geschlossen")
        return
        
        
        
       
class Warmstart_Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("Warmstart Thread wird gestartet")
        
    def run(self):
        global Kaltstart_Flag
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
        Chokehebel_fahren_Servo.move(Winkel_Chokehebel_einfahren+1)
        print("Warmstart eingestellt")
        
        Kaltstart_Flag = False
        Betrieb_Flag = False
        Warmstart_Flag = True
        
        ChangeMode_Flag = False
        
        print("Warmstart Thread wird geschlossen")
        return
        

class Betrieb_Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("Betrieb Thread wird gestartet")
        
    def run(self):
        global Kaltstart_Flag
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
            Chokehebel_fahren_Servo.move(Winkel_Chokehebel_einfahren+1)
            print("Betrieb eingestellt")
     
        Kaltstart_Flag = False
        Warmstart_Flag = False
        Betrieb_Flag = True
        
        ChangeMode_Flag = False
        print("Betrieb Thread wird geschlossen")
        return

class Motor_stopp_Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("Betrieb Thread wird gestartet")
        
    def run(self):
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

class frequence_Thread(threading.Thread):
        def __init__(self, pi, gpio, frequencedivider = 1):
            threading.Thread.__init__(self)
            print("Frequenz Thread wird gestartet")
            
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
            
class Not_Aus_class:
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
        global Zustand
        
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
            Zustand = Zustaende.Aus
            Kaltstart_Flag = False
            Warmstart_Flag = False
            Betrieb_Flag = False
                 
        if level == 1:
            sleep(2) #Sichergehen dass die BewegungsThreads geschlossen sind
            
            Relais_Setup()
            Grundstellung()
            
            Not_Aus_Flag = False
            print("Notaus geloest")    
            
    def cancel(self):
        self._cb.cancel()
  
class Zustaende(Enum):
    
    Aus = "'Aus'"
    Betrieb = "'Betrieb'"
    Warmstart = "'Warmstart'"
    Kaltstart = "'Kaltstart'"
            
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
def Grundstellung():
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

# Datenbank verbindung
def db_connection():
    global connection_counter
    connection_counter = 0
    while True:
        try:
            global cnx
            global cursor
            
            cnx = mysql.connector.connect(**db_config3)
            cursor = cnx.cursor()
            return
        except mysql.connector.Error as err:
            
            print("Database-Connection failed, Error: ", err)
            
            print("Datenbank Verbindungsversuche : {}".format(connection_counter))
            connection_counter += 1
            sleep(5)    


# Datenbankabfrage
def get_input():
    global query_input
    global Input
    global Device
    global Controlmode
    global StartStopSignal
    global Throttleposition
    global cnx
    global cursor
    
    if cnx.is_connected():
        try:
            cursor.execute(query_input)
            Input = cursor.fetchall()
            Input = Input[0]
            Device = Input[0]
            Controlmode = Input[1]
            StartStopSignal = Input[2]
            Throttleposition = Input[3]
        except mysql.connector.Error as err:
            print("Connection lost")
            print(err)
            cursor.close()
            cnx.close()
            db_connection()
    else:
        print("Connection lost")
        cursor.close()
        cnx.close()
        db_connection()           
    
        
    
#Datenbank aktualisieren
def update_output(update, value):
    global cnx
    global cursor
    
    if cnx.is_connected():
        try:
            cursor.execute(update % value)
            cnx.commit()
        except:
            print("Connection lost")
            cursor.close()
            cnx.close()
            db_connection()
            update_output(update, value)
    else:
        print("Connection lost")
        cursor.close()
        cnx.close()
        db_connection()
        update_output(update, value)

def update_output_all():
    global cnx
    global cursor
    global update_output_table
    global Zustand
    global Connection_Counter
    global Motor_an_Flag
    global Not_Aus_Flag
    
    if cnx.is_connected():
        try:
            cursor.execute(update_output_table.format(Connection_Counter, Motor_an_Flag, Zustand.value, frequence_Reader.RPM, Not_Aus_Flag))
            cnx.commit()
        except:
            print("Connection lost")
            cursor.close()
            cnx.close()
            db_connection()
    else:
        print("Connection lost")
        cursor.close()
        cnx.close()
        db_connection()



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

    
#gpio Zuweisung
pi = pigpio.pi()    

# Pinzuweisung(in GPIO)
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


# Angefahrene Winkel der Servos deklarieren, bei Werkzeugwechsel anpassen

Winkel_Chokehebel_einfahren = 2
Winkel_Chokehebel_ausfahren = 30
Winkel_Chokehebel_aus = 58
Winkel_Chokehebel_Betrieb = 19
Winkel_Chokehebel_Warmstart = -8
Winkel_Chokehebel_Kaltstart = -28
Winkel_Gas_min = -26
Winkel_Gas_Anschlag = -19
Winkel_Gas_max = 5

# Servos deklarieren (Pin, Nullstellung, min Winkel, max Winkel)

Gas_Servo = Servo(pi, Gas_GPIO,1500, Winkel_Gas_min, Winkel_Gas_Anschlag, Winkel_Gas_max)
Chokehebel_fahren_Servo = Servo(pi, Chokehebel_fahren_GPIO, 1500)
Chokehebel_drehen_Servo = Servo(pi, Chokehebel_drehen_GPIO, 1500)

# Frequenz Thread definieren

frequence_Reader = frequence_Thread(pi, Frequenz_GPIO, 2)

# Not Aus Klasse deklarieren

Not_Aus = Not_Aus_class(pi, Not_Aus_GPIO)

# Zustand deklarieren

Zustand = Zustaende.Aus

#Ausgaenge deklarieren
#Relais
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

#LEDs
pi.set_mode(LED_blue_GPIO, pigpio.OUTPUT)


# Pull Down der LEDausgaenge
pi.set_pull_up_down(LED_blue_GPIO, pigpio.PUD_DOWN)


# Nullsetzen der LED Ausgnaenge
pi.write(LED_blue_GPIO, 0)


# Flags

Kaltstart_Flag = False
Warmstart_Flag = False
Betrieb_Flag = False
ChangeMode_Flag = False
Motor_an_Flag = False
Not_Aus_Flag = False

# Datenbankkonfiguration

# Munirahs DB

db_config1 = { 'user': 'sql7291661',
               'password' : '5NMuDuvLTZ',
               'host' : 'sql7.freemysqlhosting.net',
               'port' : '3306',
               'database' : 'sql7291661',
               'connect_timeout' : 5}

# Renes DB--> mit endgueltiger Struktur

db_config2 = { 'user': 'sql2295094',
               'password' : 'jJ8!xI1%',
               'host' : 'sql2.freemysqlhosting.net',
               'port' : '3306',
               'database' : 'sql2295094'}

#Daniels DB
db_config3 = { 'user': 'VisiuLdKXI',
               'password' : 'fdakQ9qTvL',
               'host' : 'remotemysql.com',
               'port' : '3306',
               'database' : 'VisiuLdKXI',
               'connect_timeout' : 5}

# Befehle fuer Datenbank request und write

query_input = "SELECT * from input"
update_Connection = "UPDATE output SET Statusconnection = %s"
update_Statusengine = "UPDATE output SET Statusengine = %s"
update_Startcounter = "UPDATE output SET Startcounter = %s"
update_mode = "UPDATE output SET StatusMode = %s"
update_RPM = "UPDATE output SET rpm = %s"
update_Not_Aus = "UPDATE output SET lokalEmergency = %s"

update_output_table = "UPDATE output SET Statusconnection = {}, Statusengine = {}, StatusMode = {}, rpm ={}, lokalEmergency = {}"

# Variabeln fuer Datenbankabfragen
#Input
Input = None
Device = None
Controlmode = None
StartStopSignal = None
Throttleposition = None
connection_counter = 0


#Output

Connection_Counter = 0
Counter = 0


# Zeit
Motor_Timer = time()
Connection_Timer = 0

# Sonstige Variablen



if __name__ == "__main__":
    frequence_Reader.start()
    db_connection()
    Relais_Setup()
    Grundstellung()
    
    
    try:
        while True:
            get_input()
            
            # Connection Scheduler
            if Connection_Timer + 0.2 < time():
                Connection_Counter += 1
                update_output_all()
                #print("Connection updatet")
                print(frequence_Reader.averagefrequence,"\t", frequence_Reader.RPM)
                Connection_Timer = time()

            
            if Device == "MS" and not Not_Aus_Flag:
                # Warm oder Kaltstart
                if not ChangeMode_Flag and Controlmode == 0 and not Kaltstart_Flag and StartStopSignal == 0 and not Not_Aus_Flag and not Motor_an_Flag:
                    ChangeMode_Flag = True
                    Kaltstart = Kaltstart_Thread()
                    Kaltstart.start()
                    Zustand = Zustaende.Kaltstart

                elif not ChangeMode_Flag and Controlmode == 1 and not Warmstart_Flag and StartStopSignal == 0 and not Not_Aus_Flag and not Motor_an_Flag:
                    ChangeMode_Flag = True
                    Warmstart = Warmstart_Thread()
                    Warmstart.start()
                    Zustand = Zustaende.Warmstart

                elif not ChangeMode_Flag and Controlmode == 3 and not Betrieb_Flag and StartStopSignal == 0 and not Not_Aus_Flag and not Motor_an_Flag:
                    ChangeMode_Flag = True
                    Betrieb = Betrieb_Thread()
                    Betrieb.start()
                    Zustand = Zustaende.Betrieb

                    
                # Motor starten       
                if (Kaltstart_Flag or Warmstart_Flag or Betrieb_Flag) and StartStopSignal == 1 and not Motor_an_Flag and not Not_Aus_Flag and not ChangeMode_Flag:
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
                                Zustand = Zustaende.Betrieb
                            continue
                        
                        # Bei 5 Startversuchen in Warm oder Kaltstart auf Betrieb umschalten 
                        if Counter == 5 and (Kaltstart_Flag or Warmstart_Flag) and StartStopSignal == 1 and not Motor_an_Flag and not Not_Aus_Flag and not ChangeMode_Flag:
                            ChangeMode_Flag = True
                            print("Fuenf Startversuche in Warm/Kaltstart, umstellen auf Betrieb")
                            Betrieb = Betrieb_Thread()
                            Betrieb.start()
                            Zustand = Zustaende.Betrieb
                            continue
                    
                    if Motor_Timer + 15 < time():
                        LED_starting()
                        Counter += 1
                        Motor_Timer = time()
                        print("Motor Start\n Anzahl Startversuche: {}".format(Counter))
                        
                elif StartStopSignal == 0:
                    Counter = 0
                
 
                 # Gassteuerung aktivieren
                if (Kaltstart_Flag or Warmstart_Flag or Betrieb_Flag) and Motor_an_Flag and Gas_Servo.Prozent != Throttleposition and not Not_Aus_Flag:
                    print("aktuelles Gas in Prozent: ", Throttleposition)
                    Gas_Servo.gas_prozent(Throttleposition)
                
                #Motor ausschalten
                if Motor_an_Flag and (StartStopSignal == 0 or frequence_Reader.RPM == 0) and not Not_Aus_Flag:
                    print("Motor war an, ausstellen")
                    ChangeMode_Flag = True
                    Motor_an_Flag = False
                    LED_off()
                    Counter = 0
                    Motor_stopp = Motor_stopp_Thread()
                    Motor_stopp.start()
                    Zustand = Zustaende.Aus


                    

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
        if cnx.is_connected():
            cursor.close()
            cnx.close()
        
        
        
 
"""