from tkinter import *
import tkinter as tk
from tkinter import ttk
from pylsl import StreamInlet, resolve_stream, StreamInfo, StreamOutlet
import time

running = True

def stop1():
    global running
    
    if running == False:
        running = True
        print("now true")
    else:
        running = False
        print("now false")
        mysample = [0,9999999]
        outlet.push_sample(mysample)
        
def stop2():
    global running
    if running == False:
        running = True
        print("now true")
    else:
        running = False
        print("now false")
        mysample = [0,9999999]
        outlet.push_sample(mysample)

def ba_transmit1():
    global running, sample
    if running == True:
        speed = e_speed.get()
        mysample = [0,float(speed),0]
        outlet.push_sample(mysample)
        print("transmit")

def ba_transmit2():
    global running
    if running == True:
        throttle = e_throttle.get()
        mysample = [1,0,float(throttle)]
        outlet.push_sample(mysample)
        print("transmit")
        
def ba_plus_speed1():
    tmpspeed = e_speed.get()
    e_speed.delete(0, END)
    e_speed.insert(0, int(tmpspeed) + 1)

def ba_minus_speed1():
    if int(e_speed.get()) > 0:
        tmpspeed = e_speed.get()
        e_speed.delete(0, END)
        e_speed.insert(0, int(tmpspeed) - 1)

def ba_plus_speed2():
    tmpspeed = e_throttle.get()
    e_throttle.delete(0, END)
    e_throttle.insert(0, int(tmpspeed) + 1)


def ba_minus_speed2():
    if int(e_speed.get()) > 0:
        tmpspeed = e_throttle.get()
        e_throttle.delete(0, END)
        e_throttle.insert(0, int(tmpspeed) - 1)


def on_tab_selected(event):
        selected_tab=event.widget.select()
        tab_text=event.widget.tab(selected_tab, "text")

        if tab_text == "Speed Mode":
            print("Speed Mode tab selected")
        if tab_text == "Angle Mode":
            print("Angle Mode tab selected")

window = tk.Tk()
window.title("Sternfeuerung 1.0 Beta")


#=====================Setting Tab 1 and Tab 2============================# 
tab_parent=ttk.Notebook(window)

tab1=ttk.Frame(tab_parent)
tab1.grid()
tab2=ttk.Frame(tab_parent)
tab2.grid()

tab_parent.bind("<<NotebookTabChanged>>", on_tab_selected)
tab_parent.add(tab1, text="Speed Mode")
tab_parent.add(tab2, text="Angle Mode")

feedbackspeed = StringVar()
check1 = IntVar()
check1.set(0)

#=========================Tab 1: Speed Mode=============================#
l_speed = tk.Label(tab1, text="Target speed")
l_cspeed = tk.Label(tab1, text="Current speed")
l_cspeedvalue = Label(tab1, textvariable=feedbackspeed)
l_cspeedunit = tk.Label(tab1, text="m/s")
l_pthrottle = tk.Label(tab1, text="Throttle position")
l_pthrottleunit = tk.Label(tab1, text="deg")
e_speed = tk.Entry(tab1, bd=5, width=40, )
b_transmit = ttk.Button(tab1, text="transmit", command=ba_transmit1)
b_plus_speed1 = ttk.Button(tab1, text="+", command=ba_plus_speed1)
b_minus_speed1 = ttk.Button(tab1, text="-", command=ba_minus_speed1)
c_connection = ttk.Checkbutton(tab1, text="Connected",variable=check1)
stop1 = ttk.Button(tab1, text="STOP", command=stop1)

stop1.grid(row=6, column=3)
l_speed.grid(row = 0, column = 0, sticky='w')
e_speed.grid(row = 0, column = 1)
b_transmit.grid(row = 0, column = 2)
b_plus_speed1.grid(row = 1, column = 3)
b_minus_speed1.grid(row = 1, column = 2)
l_cspeed.grid(row = 2, column = 0,  sticky='w')
l_cspeedvalue.grid(row = 2, column = 1)
l_cspeedunit.grid(row = 2, column = 2)
l_pthrottle.grid(row = 3, column = 0)
l_pthrottleunit.grid(row = 3, column = 2)
c_connection.grid(columnspan=2,  sticky='w')


#=======================Tab 2: Angle Mode==============================#
l_cspeed = tk.Label(tab2, text="Current speed")
l_throttle = tk.Label(tab2, text="Manual throttle")
l_cspeedvalue = Label(tab2, textvariable=feedbackspeed)
l_cspeedunit = tk.Label(tab2, text="m/s")
l_pthrottle = tk.Label(tab2, text="Throttle position")
l_pthrottleunit = tk.Label(tab2, text="deg")
e_throttle = tk.Entry(tab2, bd=5, width=40, )
b_transmit = ttk.Button(tab2, text="transmit", command=ba_transmit2)
b_plus_speed2 = ttk.Button(tab2, text="+", command=ba_plus_speed2)
b_minus_speed2 = ttk.Button(tab2, text="-", command=ba_minus_speed2)
c_connection = ttk.Checkbutton(tab2, text="Connected",variable=check1)
stop2 = ttk.Button(tab2, text="STOP", command=stop2)

stop2.grid(row=6, column=3)
b_transmit.grid(row = 0, column = 2)
b_plus_speed2.grid(row = 1, column = 3)
b_minus_speed2.grid(row = 1, column = 2)
l_throttle.grid(row = 0, column = 0)
e_throttle.grid(row = 0, column = 1)
l_cspeed.grid(row = 2, column = 0,  sticky='w')
l_cspeedunit.grid(row = 2, column = 2)
l_pthrottle.grid(row = 3, column = 0)
l_pthrottleunit.grid(row = 3, column = 2)
c_connection.grid(columnspan=2,  sticky='w')
l_cspeedvalue.grid(row = 2, column = 1)


window.grid_rowconfigure(0, minsize=40)
window.grid_rowconfigure(1, minsize=40)
window.grid_rowconfigure(2, minsize=80)
window.grid_rowconfigure(3, minsize=20)
window.grid_rowconfigure(4, minsize=40)
window.grid_rowconfigure(5, minsize=40)
window.grid_columnconfigure(2, minsize=200)


e_speed.insert(0, 0)
e_throttle.insert(0, 0)

tab_parent.pack(expand=1, fill='both')

window.update_idletasks()
window.update()


#Create output stream
info = StreamInfo('BioSemi', 'EEG', 3, 100, 'float32', '1')
outlet = StreamOutlet(info)
#Search input stream
print("looking for a backstream...")
streams = resolve_stream('type', 'backstream')
inlet = StreamInlet(streams[0])
print("backstream found!")
check1.set(1)
#set checkbox


#window.mainloop()


while(True):
    window.update_idletasks()
    window.update()

    #pulling (receiving) the newest bit of data
    indata = None
    while True:
        lastindata = indata
        indata, timestamp = inlet.pull_sample(0)
        if (indata == None):
            indata = lastindata
            break

    if not (indata == None):
        print(indata)
        feedbackspeed
        feedbackspeed.set(indata[0])

    time.sleep(0.02)
