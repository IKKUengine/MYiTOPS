import RPi.GPIO as GPIO
import time
 
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
coil_A_1_pin = 13 # pink
coil_A_2_pin = 24 # orange
coil_B_1_pin = 18 # blau
coil_B_2_pin = 23 # gelb
#enable_pin   = 7 # Nur bei bestimmten Motoren benoetigt (+Zeile 24 und 30)
 
 
#GPIO.setup(enable_pin, GPIO.OUT)
GPIO.setup(coil_A_1_pin, GPIO.OUT)
GPIO.setup(coil_A_2_pin, GPIO.OUT)
GPIO.setup(coil_B_1_pin, GPIO.OUT)
GPIO.setup(coil_B_2_pin, GPIO.OUT)
 

GPIO.output(coil_A_1_pin, 0)
GPIO.output(coil_A_2_pin, 0)
GPIO.output(coil_B_1_pin, 0)
GPIO.output(coil_B_2_pin, 0)
