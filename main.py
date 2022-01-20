#!/bin/bash/python3 

# Pin mappings:
# 
# leftFlood = 23
# rightSpot = 24

from guizero import *
from power_api import SixfabPower, Definition, Event
from datetime import datetime
import RPi.GPIO as GPIO
import tk

# Define app first thing so we can start printing messages
#   and set fullscreen to true
app = App(title="horse_GUI")
app.tk.attributes("-fullscreen",True)

# Connect to the power hat
api = SixfabPower()

# Assume all pins are set low //might be a problem later?
pinState = [0] * 32

# Count with board before we do pins
try: 
    GPIO.setmode(GPIO.BOARD)
except:
    app.error("during GPIO.setmodexception:", "")

def updateUserConsole(message):
    userConsole.append("[" + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "] - " + message)
    userConsole.tk.see("end")

def togglePin(pinId, *args):
    if args:
        updateUserConsole("Would try to put " + str(args))
    else:
        updateUserConsole("Pin on" + str(pinId))
        """
        if pinState[pinId]:
            try:
                GPIO.output(pinId, GPIO.LOW)
                pinState[pinId] = 0
                pinSetMsg = pinId + "set low"
                updateUserConsole(pinSetMsg)
            except:
                app.error("during togglePin:", "")
        else:
            GPIO.output(pinId, GPIO.HIGH)
            pinState[pinId] = 1
            pinSetMsg = pinId + "set high"
            updateUserConsole(pinSetMsg)
        """

def refreshPowerStats():
    battLvl = Text(glance, text="Battery Level: " + str(api.get_battery_level()), align="left")
    sysTemp = Text(temps, text="System Temp: " + str(api.get_system_temp()), align="left")
    battTemp = Text(temps, text="Battery Temp: " + str(api.get_battery_temp()))
    inputTemp = Text(temps, text="Input Temp: " + str(api.get_input_temp()))
    inputVolt = Text(power, text="Input Voltage: " + str(api.get_input_voltage()))
    inputCurrent = Text(power, text="Input Current: " + str(api.get_input_current()))
    inputPower = Text(power, text="Input Power: " + str(api.get_input_power()))              #Required delay #default 50
    sysVolt = Text(power, text="System Voltage: " + str(api.get_system_voltage()))
    sysCurrent = Text(power, text="System Current: " + str(api.get_system_current()))        #Required delay #default 50
    battVolt = Text(power, text="Battery Voltage: " + str(api.get_battery_voltage()))
    battCurr = Text(power, text="Battery Current: " + str(api.get_battery_current()))
    fanHealth = Text(fans, text="Fan Health: " + str(api.get_fan_health()))
    fanSpeed = Text(fans, text="Fan Speed: " + str(api.get_fan_speed()))

def exitApp():
    app.destroy()

# Pad the left, right, top and bottom edges with 15px
topMargin = Box(app, height=15, width=1000)
leftMargin = Box(app, height=800, width=15, align="left")
rightMargin = Box(app, height=800, width=15, align="right")
bottomMargin = Box(app, height=15, width=1000, align="bottom")

# Create a box to contain the controls and lights
topThird = Box(app, width="fill", height="200")

# Status widgets
controls = TitleBox(topThird, text="horseGUI", align="left", height="fill", width="fill")
#controlsTopPadding = Box(controls, height="15", width="fill")
controlsLeftPadding = Box(controls, height="fill", width="15", align="left")
exit = PushButton(controls, text="EXIT", command=exitApp, align="left")
controlsRightPadding = Box(controls, height="fill", width="15", align="right")
controlsBottomPadding = Box(controls, height="15", width="fill")
exit.bg = "red"
exit.text_color = "white"
exit.text_size = "18"
#status.repeat(1000, refreshPowerStats)

# Lights/button widgets
lights = TitleBox(topThird, text="Lights", layout="grid", height="fill", width="fill")
lightsPaddingTop = Box(lights, height=15, width="fill", grid=[0,0])
lightsLeftPadding = Box(lights, height="fill", width="15", align="left", grid=[0,1])
button1 = PushButton(lights, text="LEFT - Flood", command=togglePin, args=[23], grid=[1,1])
button2 = PushButton(lights, text="TOGGLE\nALL", command=togglePin, args=["Both"], grid=[2,1])
button3 = PushButton(lights, text="RIGHT - Spot", command=togglePin, args=[24], grid=[3,1])
lightsRightPadding = Box(lights, height="fill", width="15", align="right", grid=[4,1])
lightsPaddingBot = Box(lights, height=15, width=15, grid=[0,2])

# Create a box to contain status and messages
botThird = Box(app, width="fill", height="fill")

status = TitleBox(botThird, text="Status", align="left", width="fill", height="fill")
statusPageButtons=Box(status, height="50", width="500")
statusPrev = PushButton(statusPageButtons, text="<", width="fill")
statusNext = PushButton(statusPageButtons, text=">", width="fill")
#statusPaddingTop = Box(status, height=15, width=15)
glance = TitleBox(status, text="At-A-Glance")
temps = TitleBox(status, text="Temperatures")
power = TitleBox(status, text="Power")
fans = TitleBox(status, text="Fans")
#status.repeat(1000, refreshPowerStats)

# Messages
messages = TitleBox(botThird, text="Messages", width="fill", height="fill")
userConsole = TextBox(messages, text="Starting up...", align="left", multiline=True, height="fill", width="fill", scrollbar=True)
userConsole.bg = "black"
userConsole.text_color = "white"
userConsole.text_size = "18"
messagePaddingBot = Box(messages, height=15, width=15)

app.display()