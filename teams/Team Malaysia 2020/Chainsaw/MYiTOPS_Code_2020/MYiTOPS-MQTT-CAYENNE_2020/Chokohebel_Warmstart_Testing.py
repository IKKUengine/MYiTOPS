import pigpio                           #Install every library here in common library path
from enum import Enum
from time import sleep
from time import time
import threading
import cayenne.client

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

pi = pigpio.pi()

Chokehebel_drehen_GPIO = 18

Chokehebel_drehen_Relais_GPIO = 25

Winkel_Chokehebel_Warmstart = -8

Chokehebel_drehen_Servo = Servo(pi, Chokehebel_drehen_GPIO, 1500)

pi.set_mode(Chokehebel_drehen_Relais_GPIO, pigpio.OUTPUT)

pi.set_pull_up_down(Chokehebel_drehen_Relais_GPIO, pigpio.PUD_DOWN)

pi.write(Chokehebel_drehen_Relais_GPIO, 0)

pi.write(Chokehebel_drehen_Relais_GPIO, 1)
print("Chokehebel fahren Relais zugeschalten")
sleep(0.5)

Chokehebel_drehen_Servo.move(Winkel_Chokehebel_Warmstart)




