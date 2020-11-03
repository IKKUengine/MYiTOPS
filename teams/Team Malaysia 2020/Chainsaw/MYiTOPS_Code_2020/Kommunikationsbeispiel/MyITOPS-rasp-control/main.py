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

from enum import Enum


mqttclient_log=False #MQTT client logs showing messages
logging.basicConfig(level=logging.INFO) #Error logging
settings=dict()
subscriber_dict=dict()
publisher_dict=dict()

# quality of service --> publish-feature
qosAtMostOnce = 0 # Parameter als Konstanten defieniert
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
settings["port"]=1883 # MQTT broker port von der internationaller Stelle festgelegt
settings["clientname"]="MQTT-EMS-MYITOPS-Control" # Set client name or this instance name

topicEngineControl = "HsKA/IKKULab/IKKULab043/CPS/EngineControl" # eine def der Nachrichten art als String
topicEngineSensorInfo = "HsKA/IKKULab/IKKULab043/CPS/EngineSensorInfo"
settings["topics"]=[(topicEngineSensorInfo, qosExactlyOnce)] # zur Z.41 ich habe es getrennt gemacht, hier können ale von uns abonierte Topics auf ein mal übergeben 

class Zustaende(Enum):
    Aus = "'Aus'"
    Betrieb = "'Betrieb'"
    Warmstart = "'Warmstart'"
    Kaltstart = "'Kaltstart'"
    
class FrequenceReader:
    RPM = 0
    
Connection_Counter = 0
Motor_an_Flag = False
Not_Aus_Flag = False
Zustand = Zustaende.Aus
frequence_Reader = FrequenceReader

#### Publish to topic
def publishing_message():
    ControlMode = random.randrange(0, 2)
    StartStopSignal = random.randrange(0, 1)
    Throttleposition = random.randrange(0, 100)

    # Change the value inside here
    publisher_dict = {"Publisher": "R.Pi-MYITOPS-CONTROL", 
                      "Device": "MS",
                      "ControlMode": str(ControlMode),
                      "StartStopSignal": str(StartStopSignal),
                      "Throttleposition": str(Throttleposition) }


    publisher_json = json.dumps(publisher_dict)
#    print(publisher_json)

    client.publish(topicEngineControl, publisher_json, qos=qosExactlyOnce)


def on_disconnect(client, userdata, rc):
   logging.debug("disconnecting reason " + str(rc))
   client.connected_flag = False
   client.disconnect_flag = True
   client.subscribe_flag = False


def on_connect(client, userdata, flags, rc):
   logging.debug("Connected flags" + str(flags) + "result code " \
                 + str(rc) + "client1_id")
   if rc == 0:# wenn es geklappt hat ist rc==0 dann ist der connected Flag auf true sonst bad connected auf true
      client.connected_flag = True
      print("Connected to broker: " + settings["broker"])
   else:
      client.bad_connection_flag = True


def on_subscribe(client, userdata, mid, granted_qos):
   m = "in on subscribe callback result " + str(mid)
   logging.debug(m)
   client.subscribed_flag = True

#### Subcribing message
def on_message(client, userdata, message):
   global Connection_Counter
   global Motor_an_Flag
   global Not_Aus_Flag
   global Zustand
   global frequence_Reader
   
   subscriber_dict = json.loads(str(message.payload.decode("utf-8", "ignore")))  # Convert json message
   if message.topic == topicEngineSensorInfo:
       print("received message:")
       Publisher = subscriber_dict["Publisher"]
       Connection_Counter = int(subscriber_dict["Connection_Counter"])
       Motor_an_Flag = bool(subscriber_dict["Motor_an_Flag"])
       Zustand = Zustaende[subscriber_dict["Zustand"]]
       frequence_Reader.RPM = float(subscriber_dict["RPM"])
       Not_Aus_Flag = bool(subscriber_dict["Not_Aus_Flag"])
       
       print(Publisher)
       print(Connection_Counter)
       print(Motor_an_Flag)
       print(Zustand)
       print(frequence_Reader.RPM)
       print(Not_Aus_Flag)

def on_log(client, userdata, level, buf): # Fehlerausgabe
   print(userdata)

def Initialise_clients(clientname, cleansession=True):
   # flags setd
   client = mqtt.Client(clientname)
   client.connected_flag=False #  flag for connection
   client.bad_connection_flag=False
   client.subscribed_flag=False
   if mqttclient_log:  # enable mqqt client logging, Fehlermeldung
      client.on_log = on_log
      
   # callbacks
   client.on_connect = on_connect  # attach function to callback
   client.on_message = on_message  # attach function to callback
   client.on_disconnect = on_disconnect
   client.on_subscribe = on_subscribe
   
   return client


#### Main program
if not settings["clientname"]:# falls kein clientname wird eins erzeugt 
    r=random.randrange(1,10000)
    clientname="IKKULabEMS-"+str(r)
else:
    clientname="IKKULabEMS-"+str(settings["clientname"])#falls vorhanden wird hier angehängt

#### Initialise_client_object() #  add extra flags

logging.info(" creating client "+clientname)#
client=Initialise_clients(clientname,False) # create and initialise client object

if settings["username"] !="":
    print("setting broker's username:",settings["username"],"and password:",settings["password"])
    client.username_pw_set(settings["username"], settings["password"])

client.connect(settings["broker"],settings["port"])
# zwei Parameter werden hier übergeben client.connect(settings["broker"], settings["port"], settings["keepalive"]))
client.loop_start() #Verbindungsaufbau

while not client.connected_flag: # wait for connection
    print("waiting for connection")
    time.sleep(1) #Achtung keine Endlosschleife.diese wird von der call back Routine on subscribe unterbrochen 

client.subscribe(settings["topics"])

while not client.subscribed_flag: # wait to subscribe to topic
    print("waiting for subscribe")
    time.sleep(1)

print("subscribed topic:",settings["topics"])


#### loop and wait until interrupted
try:
    while True:
        time.sleep(10)
        publishing_message()
       
except KeyboardInterrupt:
    print("interrrupted by keyboard")

####

client.loop_stop()  # final check for messages
time.sleep(5)

print("program stop")

