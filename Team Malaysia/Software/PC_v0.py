import time
from tkinter import *

from pylsl import StreamInfo, StreamOutlet

def ba_transmit():
    speed = e_speed.get()
    mysample = [float(speed)]
    outlet.push_sample(mysample)    
def ba_plus_speed():
    tmpspeed = e_speed.get()
    e_speed.delete(0, END)
    e_speed.insert(0, int(tmpspeed) + 1)
def ba_minus_speed():
    if int(e_speed.get()) > 0:
        tmpspeed = e_speed.get()
        e_speed.delete(0, END)
        e_speed.insert(0, int(tmpspeed) - 1)

window = Tk()
window.title("transmitter")

currentspeed = StringVar()
currentthrottleposition = StringVar()

l_speed = Label(window, text="speed")
l_cspeed = Label(window, text="Current speed")
l_cspeedvalue = Label(window, textvariable=currentspeed)
l_cspeedunit = Label(window, text="m/s")
l_pthrottle = Label(window, text="Throttle position")
l_pthrottlevalue = Label(window, textvariable=currentthrottleposition)
l_pthrottleunit = Label(window, text="deg")
e_speed = Entry(window, bd=5, width=40, )
b_transmit = Button(window, text="transmit", command=ba_transmit)
b_plus_speed = Button(window, text="+", command=ba_plus_speed)
b_minus_speed = Button(window, text="-", command=ba_minus_speed)
l_speed.grid(row = 0, column = 0)
e_speed.grid(row = 0, column = 1)
b_transmit.grid(row = 0, column = 2)
b_plus_speed.grid(row = 1, column = 1)
b_minus_speed.grid(row = 1, column = 2)
l_cspeed.grid(row = 2, column = 0)
l_cspeedvalue.grid(row = 2, column = 1)
l_cspeedunit.grid(row = 2, column = 2)
l_pthrottle.grid(row = 3, column = 0)
l_pthrottlevalue.grid(row = 3, column = 1)
l_pthrottleunit.grid(row = 3, column = 2)

e_speed.insert(0, 0)

info = StreamInfo('BioSemi', 'EEG', 1, 100, 'float32', 'myuid34234')

outlet = StreamOutlet(info)

for x in range(0, 4):
    currentspeed.set(x)
    currentthrottleposition.set("rr")

#while(True):
#    currentspeed.set("rr")
#    currentthrottleposition.set("rr")
#    print("done")
#    time.sleep(1)
