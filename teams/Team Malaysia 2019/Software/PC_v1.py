import time
from tkinter import *
from tkinter import ttk

from pylsl import StreamInlet, resolve_stream, StreamInfo, StreamOutlet

def ba_transmit():
    speed = e_speed.get()
    mysample = [0,float(speed)]
    outlet.push_sample(mysample)

    sample, timestamp = inlet.pull_sample(1)
    print(timestamp, sample)
    
def ba_plus_speed():
    tmpspeed = e_speed.get()
    e_speed.delete(0, END)
    e_speed.insert(0, int(tmpspeed) + 10)
def ba_minus_speed():
    if int(e_speed.get()) > 0:
        tmpspeed = e_speed.get()
        e_speed.delete(0, END)
        e_speed.insert(0, int(tmpspeed) - 10)

window = Tk()

window.title("Sternfeuerung 1.0 Beta")

currentspeed = StringVar()
currentthrottleposition = StringVar()

myStyle=ttk.Style()
print(myStyle.theme_names())
myStyle.theme_use('clam')



l_speed = Label(window, text="Target speed")
l_cspeed = Label(window, text="Current speed")
l_cspeedvalue = Label(window, textvariable=currentspeed)
l_throttle = Label(window, text="Manual throttle")
l_cspeedunit = Label(window, text="m/s")
l_pthrottle = Label(window, text="Throttle position")
l_pthrottlevalue = Label(window, textvariable=currentthrottleposition)
l_pthrottleunit = Label(window, text="deg")
e_speed = Entry(window, bd=5, width=40, )
e_throttle = Entry(window, bd=5, width=40, )
b_transmit = ttk.Button(window, text="transmit", command=ba_transmit)
b_plus_speed = ttk.Button(window, text="+", command=ba_plus_speed)
b_minus_speed = ttk.Button(window, text="-", command=ba_minus_speed)
c_connection = Checkbutton(window, text="Connected",variable=1)
l_speed.grid(row = 0, column = 0)
e_speed.grid(row = 0, column = 1)
b_transmit.grid(row = 0, column = 2)
b_plus_speed.grid(row = 1, column = 3)
b_minus_speed.grid(row = 1, column = 2)
l_throttle.grid(row = 2, column = 0)
e_throttle.grid(row = 2, column = 1)
l_cspeed.grid(row = 3, column = 0)
l_cspeedvalue.grid(row = 3, column = 1)
l_cspeedunit.grid(row = 3, column = 2)
l_pthrottle.grid(row = 4, column = 0)
l_pthrottlevalue.grid(row = 4, column = 1)
l_pthrottleunit.grid(row = 4, column = 2)
c_connection.grid(columnspan=2, sticky=W)


window.grid_rowconfigure(0, minsize=40)
window.grid_rowconfigure(1, minsize=40)
window.grid_rowconfigure(2, minsize=80)
window.grid_rowconfigure(3, minsize=20)
window.grid_rowconfigure(4, minsize=40)
window.grid_rowconfigure(5, minsize=40)
window.grid_columnconfigure(2, minsize=200)
#window.configure(background='grey')


e_speed.insert(0, 0)


#                                                               Create output stream
info = StreamInfo('BioSemi', 'EEG', 2, 100, 'float32', '1')
outlet = StreamOutlet(info)
#                                                               Search input stream
#print("looking for a backstream...")
#streams = resolve_stream('type', 'backstream')
#print("...found one! *__* <3 ")
#inlet = StreamInlet(streams[0])

window.mainloop()

#for x in range(0, 4):
#    currentspeed.set(x)
#    currentthrottleposition.set("rr")

#while(True):
#    currentspeed.set("rr")
#    currentthrottleposition.set("rr")
#    print("done")
#    time.sleep(1)
