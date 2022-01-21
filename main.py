#!/bin/bash/python3 

from guizero import *
from power_api import SixfabPower, Definition, Event
from rpi_backlight import Backlight
from datetime import datetime
import RPi.GPIO as GPIO
import tk

# Define app first thing and set fullscreen to true
app = App(title="horse_GUI")
app.tk.attributes("-fullscreen",True)

# Do library setups
api = SixfabPower()
bl = Backlight()

# Assume all pins are set low //might be a problem later?
pinState = [0] * 32

# Count with board before we do pins
try: 
    GPIO.setmode(GPIO.BOARD)
except:
    app.error("during GPIO.setmodexception:", "")

##########
# Function definitions
##########

def updateUserConsole(message):
    userConsole.append("[" + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "] - " + message)
    userConsole.tk.see("end")

def handleButton(pushList):
    for push in pushList: # Run for every item passed
        if type(push) == int:
            togglePin(push)

def togglePin(pinId):
    #updateUserConsole("Toggle " + str(pinId))
    pins[pinId].toggle()

def setEmission(emissionLevel):
    if emissionLevel == 0:
        updateUserConsole("Set Condition 0: Emission Prohibited")
        emissionIndicator.bg = "red"
        emissionIndicatorText.text_color = "white"
        emissionIndicatorText.value = "E/C:\n0"
    if emissionLevel == 1:
        updateUserConsole("Set Condition 1: Quiet listening")
        emissionIndicator.bg = "green"
        emissionIndicatorText.text_color = "white"
        emissionIndicatorText.value = "E/C:\n1"
    if emissionLevel == 2:
        updateUserConsole("Set Condition 2: Unrestricted Emission")
        emissionIndicator.bg = "blue"
        emissionIndicatorText.text_color = "white"
        emissionIndicatorText.value = "E/C:\n2"

def toggleBacklight(escape):
    if escape:
        updateUserConsole("Turning backlight on.")
        bl.brightness = 25
        bl.power = True
        backlightWindow.hide()
        return
    elif bl.brightness != 100:
        updateUserConsole("Turning backlight up.")
        bl.brightness = 100
    else:
        updateUserConsole("Turning backlight off.")
        bl.power = False
        backlightWindow.show()

def updateGlance():
    localInputVolt = api.get_input_voltage()
    localBattLvl = api.get_battery_level()
    #updateUserConsole("A/C: "+ str(round(localInputVolt, 2)))
    #updateUserConsole("Battery: " + localBattLvl)
    try:
        inputLvl.value = "Input:\n" + str(round(localInputVolt, 2)) + "v"
    except:
        inputLvl.value = "Input:\nerr"
    try:
        battLvl.value = "Battery:\n" + str(localBattLvl) + "%"
    except:
        battLvl.value = "Battery:\nerr"
   
    '''
    if float(inputLvl.value) - localInputVolt == inputLvl.value:
        updateUserConsole("A/C connection lost.")
    if float(inputLvl.value) + localInputLvl != 0.0:
        updateUserConsole("A/C connection gained.")
    '''

    if localInputVolt == 0.0:
        inputLvl.bg = "red"
    elif localInputVolt >= 4.0:
        inputLvl.bg = "green"
        battLvl.bg = "blue"

    if localInputVolt == 0.0 and localBattLvl >= 80:
        battLvl.bg = "green"
    elif localInputVolt == 0.0 and localBattLvl >= 40 and localBattLvl < 80:
        battLvl.bg = "orange"
    elif localInputVolt == 0.0 and localBattLvl < 40:
        battLvl.bg = "red"

    '''
    inputVolt = Text(power, text="Input Voltage: " + str(api.get_input_voltage()))
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
    '''

def displayBattLvl():
    battLvlBlock = Box(glance, text=battLvl)

def exitApp():
    app.destroy()

# Set up for backlight control
backlightWindow = Window(app, title="Tap to turn on backlight")
closeBacklightWindow = PushButton(backlightWindow, height="fill", width="fill", text="Tap to turn on backlight", command=toggleBacklight, args=[True])
backlightWindow.tk.attributes("-fullscreen",True)
backlightWindow.hide()

# Our functions are now defined, let's map pins

pins = dict()

# Class of MappedPin for looking up which button is mapped to a pin
#   for lookups and callbacks
#   This is for altering the button background in handleButton()
class MapPin:
    def __init__(self, pin_no, button, deviceName):
        self.button = button
        self.pin = pin_no
        self.state = "low"
        self.deviceName = deviceName
 
    def __eq__(self, other):
       
        # Equality Comparison between two objects
        return self.name == other.name and self.pin == other.pin

    def toggle(self):
        if self.state == "low":
            self.button.bg = "yellow"
            self.state = "high"
            updateUserConsole("Turned " + self.deviceName + " on.")
        else:
            self.state = "low"
            self.button.bg = None
            updateUserConsole("Turned " + self.deviceName + " off.")
#######
# Begin to build the document
#######

# Pad the left, right, top and bottom edges with 15px
topMargin = Box(app, height=15, width=1000)
leftMargin = Box(app, height=800, width=15, align="left")
rightMargin = Box(app, height=800, width=15, align="right")
bottomMargin = Box(app, height=15, width=1000, align="bottom")

# Create a box to contain the controls and lights
topThird = Box(app, width="fill", height="200")

# Control widget
controls = TitleBox(topThird, text="horseGUI", align="left", height="fill", width="fill", layout="grid")
controls.text_size = 14
#controlsTopPadding = Box(controls, height="15", width="fill")
controlsLeftPadding = Box(controls, height="fill", width="15", grid=[0,0])

# Device controls
appControls = Box(controls, grid=[1,0], layout="grid")
exit = PushButton(appControls, text="EXIT", command=exitApp, grid=[0,0])
backlight = PushButton(appControls, text="BACKLIGHT", command=toggleBacklight, args=[False],grid=[1,0])

# Emission controls
emissionControl = TitleBox(controls, text="E/C - Emission Control", border=False, grid=[1,1], layout="grid")
emission0 = PushButton(emissionControl, text="CONDITION 0", command=setEmission, args=[0], grid=[0,0])
emission1 = PushButton(emissionControl, text="LISTEN", command=setEmission, args=[1], grid=[1,0])
emission2 = PushButton(emissionControl, text="LOUD", command=setEmission, args=[2], grid=[2,0])

# Controls padding
controlsRightPadding = Box(controls, height="fill", width="15", grid=[3,1])
controlsBottomPadding = Box(controls, height="15", width="fill", grid=[0,4])

# Controls color settings
exit.bg = "red"
exit.text_color = "white"
exit.text_size = "18"
backlight.bg = "black"
backlight.text_color = "white"
backlight.text_size = "16"
emission0.bg = "gray"
emission0.text_color = "white"
emission1.bg = "green"
emission1.text_color = "white"
emission2.bg = "blue"
emission2.text_color = "white"

# Lights/button widgets
lights = TitleBox(topThird, text="Lights", layout="grid", height="fill", width="fill")
lights.text_size = 14
lightsPaddingTop = Box(lights, height=15, width="fill", grid=[0,0])
lightsLeftPadding = Box(lights, height="fill", width="15", align="left", grid=[0,1])
leftFloodButton = PushButton(lights, text="LEFT - Flood", command=handleButton, args=[[23]], grid=[1,1])
toggleBothButton = PushButton(lights, text="TOGGLE\nALL", command=handleButton, args=[[23, 24]], grid=[2,1])
rightSpotButton = PushButton(lights, text="RIGHT - Spot", command=handleButton, args=[[24]], grid=[3,1])
lightsRightPadding = Box(lights, height="fill", width="15", align="right", grid=[4,1])
lightsPaddingBot = Box(lights, height=15, width=15, grid=[0,2])

# Create a box to contain status and messages
botThird = Box(app, width="fill", height="fill")

# Status
status = TitleBox(botThird, text="Status", align="left", width="500", height="fill")
status.text_size = 14

# Glance module
glance = Box(status, height=100, width="200", layout="grid")

# Battery charge level indicator
battIndicator = Box(glance, height="70", width="70", grid=[0,0], border=True)
battIndicator.bg = "white"
battLvl = Text(battIndicator, text="Battery:\n" + str(api.get_battery_level()) + "%", height="fill", width="fill")
battLvl.text_color = "white"
battLvl.text_size = 14

# Power input indicator
inputIndicator = Box(glance, height="70", width="70", grid=[1,0], border=True)
inputIndicator.bg = "white"
try:
    inputLvl = Text(inputIndicator, text="Input:\n" + str(round(api.get_input_voltage(),2)) + "v", height="fill", width="fill")
except:
    inputLvl = Text(inputIndicator, text="Input:\nerr", height="fill", width="fill")
#inputLvl.bg = "white"
inputLvl.text_color = "white"
inputLvl.text_size = 14

# Emission control level indicator
emissionIndicator = Box(glance, height="70", width="70", grid=[0,1], border=True, align="left")
emissionIndicator.bg = "white"
emissionIndicatorText = Text(emissionIndicator, text="E/C:\nN/A", height="fill", width="fill")
emissionIndicatorText.text_color = "black"
# Restrict emissions at startup

# Status page navigation controls
statusPageButtons=Box(status, height="200", width="fill")
#statusPageButtons.bg = "gray"
statusPrev = PushButton(statusPageButtons, text="<", width="fill", align="left")
statusRefresh = PushButton(statusPageButtons, image="./refresh.png", command=updateGlance, align="left")
statusNext = PushButton(statusPageButtons, text=">", width="fill", align="left")

# Messages
messages = TitleBox(botThird, text="Messages", border=False, width="fill", height="fill")
messages.text_size = 14
messages.text_color = "white"
messages.bg = "black"
userConsole = TextBox(messages, text="System ready.", align="left", multiline=True, height="fill", width="fill", scrollbar=True)
userConsole.bg = "black"
userConsole.text_color = "white"
userConsole.text_size = "18"
messagePaddingBot = Box(messages, height=15, width=15)

# Map our buttons using the MappedPin class
#   MUST be done after buttons are defined
#   MapPin(pinId, buttonName, deviceName
pins[23] = MapPin(23, leftFloodButton, "flood light")
pins[24] = MapPin(24, rightSpotButton, "spot light")

status.repeat(2000, updateGlance)

app.display()
