import pigpio                           #Install every library here in common library path
from enum import Enum
from time import sleep
from time import time
import threading
import cayenne.client

class Servo:
    def __init__(self, pi, GPIO, Nullposition = 1500, anschlag_Winkel = 0):   # Nullpostion gibt die Mittelstellung in Pulsweite an, durch Tests bestimmt
        self.GPIO = GPIO
        self.Nullposition = Nullposition
        self.anschlag_Winkel = anschlag_Winkel
        self.Prozent = 0
        
        self.Servo_Lib = pi
        
    def move(self, Winkel): # Bewegen mit Winkel, Umrechnung auf Pulsweite
        self.Servo_Lib.set_servo_pulsewidth(self.GPIO, self.Nullposition + (Winkel * 10))
        self.Position = Winkel

pi = pigpio.pi()

Gas_GPIO = 14

# Relais
Gas_Relais_GPIO = 23

Winkel_Gas_Anschlag = -19

Gas_Servo = Servo(pi, Gas_GPIO,1500, Winkel_Gas_Anschlag)

pi.set_mode(Gas_Relais_GPIO, pigpio.OUTPUT)

# Pull Down der Relaisausgaenge
pi.set_pull_up_down(Gas_Relais_GPIO, pigpio.PUD_DOWN)

#Nullsetzen der Relaisausgaenge
pi.write(Gas_Relais_GPIO, 0)


pi.write(Gas_Relais_GPIO, 1)
print("Gas Relais zugeschalten")
sleep(0.5)
    
Gas_Servo.move(Winkel_Gas_Anschlag)


