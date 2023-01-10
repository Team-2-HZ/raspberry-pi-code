#! /usr/bin/python2

import time
import sys
import glob
from sendImg import sendImage
from captureImg import captureImg
from Adafruit_CharLCD import Adafruit_CharLCD
import RPi.GPIO as GPIO
from hx711 import HX711

# Specify the LCD connections
lcd = Adafruit_CharLCD(rs=25, en=24, d4=23, d5=17,
                       d6=27, d7=22, cols=16, lines=2)

# Set up the buttons
GPIO.setmode(GPIO.BCM)

# Specify the Button connections
WEIGH_BUTTON = 26
SEND_DETAILS_BUTTON = 19
TARE_BUTTON = 13

# Set up the button inputs
GPIO.setup(WEIGH_BUTTON, GPIO.IN)
GPIO.setup(SEND_DETAILS_BUTTON, GPIO.IN)
GPIO.setup(TARE_BUTTON, GPIO.IN)

# Set reference unit so the scale weight is calibrated to zero grams
referenceUnit = 449.324

# Set the scale's weighing function to inactive when turned on, to be updated to active using button commands later
runScales = False

# Clean the GPIO connection
def cleanAndExit():
    print("Cleaning...")

    GPIO.cleanup()

    print("Bye!")
    sys.exit()


# Refresh LCD, clearing the text and seting cursor to the start position
def refreshLcd():
    lcd.clear()
    lcd.home()


# Display the weight value from the scale
def displayWeight(weight):
    refreshLcd()
    lcd.message(weight)

# Powering down device and cleaning GPIO ports on exit    
def exitProgram():
    refreshLcd()
    lcd.message("Powering off...")
    time.sleep(3)
    refreshLcd()
    cleanAndExit()

# Identify the RPi pins connected to the scales
hx = HX711(5, 6)

# IN THE EVEN OF RANDOM VALUES - Description from original repo's author
# I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
# Still need to figure out why does it change.
# If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
# There is some code below to debug and log the order of the bits and the bytes.
# The first parameter is the order in which the bytes are used to build the "long" value.
# The second paramter is the order of the bits inside each byte.
# According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.
hx.set_reading_format("MSB", "MSB")

# HOW TO CALCULATE THE REFFERENCE UNIT - Example from original repo's author
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
# hx.set_reference_unit(113)

hx.set_reference_unit(referenceUnit)

hx.reset()

hx.tare()

print("Tare done! Add weight now...")

# The program loop when device is turned on
while True:
    try:
        refreshLcd()
        lcd.message("Press white\nbutton to begin")
        
        # Button command checks to activate the weighing functionality
        if GPIO.input(WEIGH_BUTTON):
                runScales = True
                print("Pressed the Start Weighing Button")
        elif GPIO.input(TARE_BUTTON):
                print("Pressed the Power Off Button")
                exitProgram()
        
        # Code for the scales' operation
        while runScales:
            refreshLcd()
            
            weight = hx.get_weight(5)
            print(int(weight))
            
            weightList = list()
            weightList.extend(str(int(weight)))
            weightList.append("g")
            
            if int(weight) > 0: 
                lcd.message(weightList)

            # Button command to capture an image and send the image and weight details to the APIs
            if GPIO.input(SEND_DETAILS_BUTTON):
                print("Pressed the Send Details Button")
                if weight >= 5:
                    refreshLcd()
                    lcd.message("Point Camera\nat food")
                    time.sleep(3)

                    # Call code to take photo
                    captureImg()
                    refreshLcd()
                    lcd.message("Processing...")
                    # Call code to send photo and weight details via POST request
                    print("Sending weight and photo to server")
                    sendImage(int(weight))

                    refreshLcd()
                    lcd.message("Information Sent")
                    print("Information sent")
                    time.sleep(3)
                    refreshLcd()
                    lcd.message("Check app for\nmore information")
                    print("Check app")
                    time.sleep(10)
                    refreshLcd()

                    # Set the scales to inactive
                    runScales = False
                    refreshLcd()
                    lcd.message("Restarting\nthe scale")
                    time.sleep(5)
                else:
                    print("No food on the scale")
                    refreshLcd()
                    lcd.message("No food found\non the scale")
            
            # Tare the scale weight, aka set value to zero        
            elif GPIO.input(TARE_BUTTON):
                print("Pressed the Tare Button")
                hx.tare()
            
            elif weight >= 0 and weight < 5:
                refreshLcd()
                lcd.message("Place food\non scale")
            
            # Set the scales to inactive    
            if GPIO.input(WEIGH_BUTTON):
                runScales = False
                print("Stopping the weighing")
                refreshLcd()
                lcd.message("Restarting\nthe scale")
                time.sleep(5)

            hx.power_down()
            hx.power_up()
            time.sleep(0.5)

    except (KeyboardInterrupt, SystemExit):
        exitProgram()
