#! /usr/bin/python2

import time
import sys
import glob
from sendImg import sendImage
from captureImg import captureImg
from Adafruit_CharLCD import Adafruit_CharLCD

EMULATE_HX711 = False
if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

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

referenceUnit = 449.324

sameWeight = 0

count = 0

# Clean the GPIO connection
def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
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

refreshLcd()
lcd.message("Ready to start")

# To use both channels, you'll need to tare them both
# hx.tare_A()
# hx.tare_B()

while True:
    try:
        refreshLcd()
        weight = hx.get_weight(5)
        print(int(weight))
        weightList = list()
        weightList.extend(str(int(weight)))
        weightList.append("g")
        print (GPIO.input(WEIGH_BUTTON))

        if GPIO.input(WEIGH_BUTTON):
            displayWeight(weightList)
            print("Pressed White Button")
        elif GPIO.input(SEND_DETAILS_BUTTON):
            print("Pressed Yellow Button")
            # Check if weight is not fluctuating and record the stable measurement
            if weight >= 5:
                if int(weight) != int(sameWeight):
                    sameWeight = weight
                    count = 0
                else:
                    count += 1
                    print(count)
                    if count > 6:
                        count = 0

                        refreshLcd()
                        lcd.message("Processing...")

                        # Call code to take photo
                        captureImg()

                        # Call code to send photo and weight details via POST request
                        print("Sending weight and photo to server")
                        sendImage(weight)

                        refreshLcd()
                        lcd.message("Information Sent")
                        time.sleep(3)
                        lcd.message("Check App for\nmore information")

                        cleanAndExit()
        elif GPIO.input(TARE_BUTTON):
            print("Pressed Red Button")
            hx.tare()
        elif weight >= 0 and weight < 5:
            refreshLcd()
            lcd.message("Place food\non scale")

        hx.power_down()
        hx.power_up()
        time.sleep(0.5)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
