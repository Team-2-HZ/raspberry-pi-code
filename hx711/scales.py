#! /usr/bin/python2

# New refactored version of example.py with methods
# For additional documentation and comments on how to set up and run the code, see example.py
# Comments below are related to the code in use.

import time
import sys
import requests

EMULATE_HX711=False

# Select appropriate hx711 file
if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

# Calibration value for accurate scale measurements
# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
referenceUnit = 449.324

# Values for triggering the POST request
itemWeight = 0
comparisonWeight = 0

# Initialise the scale settings
def initialiseScale():
    hx = HX711(5, 6)
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(referenceUnit)
    hx.reset()
    hx.tare()
    print("Tare done! Add weight now...")

    return hx

def checkWeight(hx):
    while True:
        try:
            # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
            # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
            # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment these three lines to see what it prints.
            
            # np_arr8_string = hx.get_np_arr8_string()
            # binary_string = hx.get_binary_string()
            # print binary_string + " " + np_arr8_string
            
            # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
            weight = hx.get_weight(5)
            print(weight)
            setWeight(weight)

            # To get weight from both channels (if you have load cells hooked up 
            # to both channel A and B), do something like this
            #val_A = hx.get_weight_A(5)
            #val_B = hx.get_weight_B(5)
            #print "A: %s  B: %s" % ( val_A, val_B )

            confirmItemWeight(weight)

            hx.power_down()
            hx.power_up()
            time.sleep(0.5)

        except (KeyboardInterrupt, SystemExit):
            cleanAndExit()

# Function to confirm the item weight remains constant while on the scale
# If the weight is not constant for at least 6 ticks, then it will not begin the request builder
def confirmItemWeight(weight):
    if weight > 5:            
        print("Over 5grams, checking weights")
                
        if int(weight) != int(comparisonWeight):
            comparisonWeight = weight
            count = 0
        else:
            count += 1
            if count > 6:
                count = 0
                sendPostRequest(weight)
                cleanAndExit()
    else:
        print("Weight below 5 grams, rechecking")

# Function to build and send the POST request to the server     
def sendPostRequest(weight):
    bearerTkn = 'miTQ1NwbocCI?A2uyop1?VN=l3wh?kebR6WuepYJCOFfzWqGImXfiO/Ksed5pAxQBP8km8qU!6RmhehCPlF5D7TZm?R8w4bH8JpQXxrgABVDfAHyC9yBp3M2zxCQN13-oSf-fJhqjY-X9HlyMyq6y3Rm486eOx5VGWt!upDx-Y3CorzLs747otpnGEcfOQozNoSzJqlC!PZGypR22j/2DD1jzuCml!eHjfkX=sT8lQYqabuOnAJ/fhI6HKdo1p0X'
    url = 'https://nutrition-app-weight.onrender.com/weight'
                    
    response = requests.post(
                url, 
                json = {"data": {"food" : "chicken", "grams": int(val)}},
                headers = {"Authorization": f"Bearer {bearerTkn}" })

    print("post request sent with " , int(weight))
    print(response)

# Deactivate the sensor
def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()