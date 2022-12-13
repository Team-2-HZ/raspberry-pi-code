#! /usr/bin/python2

from picamera import PiCamera
import time
import sys
import requests
import json

EMULATE_HX711=False

camera = PiCamera()

referenceUnit = 449.324

sameVal = 0

count = 0

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()

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

#hx.set_reference_unit(113)
hx.set_reference_unit(referenceUnit)

hx.reset()

hx.tare()

print("Tare done! Add weight now...")

# To use both channels, you'll need to tare them both
#hx.tare_A()
#hx.tare_B()

while True:
    try:
        # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
        val = hx.get_weight(5)
        print(val)

        # Check if weight is not fluctuating and record the stable measurement
        if val > 5:
            if int(val) != (int(sameVal) + 1) or int(val) != (int(sameVal - 1)):
                sameVal = val
                count = 0
            else:
                count += 1
                print(count)
                if count > 6:
                    count = 0
                    print("Sending weight to server") 
                    
                    # Code to call on camera and take photo
                    print("Starting Camera")
                    camera.start_preview()
                    time.sleep(5)
                    camera.capture('./processing/user_input/inputs/image_1.jpg')
                    print("Picture Captured")
                    camera.stop_preview()
                    # End of camera code
                    
                    ## TODO - Fix this to send the image to the server 
                    ## TODO - Test connection to Daniel's image recognition code
                    # Send the photo to the image recognition microservice
                    print('Sending image to the database')                    
                    imgUrl = 'https://6389cff34eccb986e89b39dd.mockapi.io/foodscan/images'
                    imgFile = { 'file': open('./processing/user_input/inputs/image_1.jpg', 'rb')}

                    imgResponse = requests.post(imgUrl, files = imgFile)
                    print(imgResponse.json)
                    print('Finished sending image\n')
                    # End of Code

                    # Send the request to the nutrition calculation microservice
                    bearerTkn = 'miTQ1NwbocCI?A2uyop1?VN=l3wh?kebR6WuepYJCOFfzWqGImXfiO/Ksed5pAxQBP8km8qU!6RmhehCPlF5D7TZm?R8w4bH8JpQXxrgABVDfAHyC9yBp3M2zxCQN13-oSf-fJhqjY-X9HlyMyq6y3Rm486eOx5VGWt!upDx-Y3CorzLs747otpnGEcfOQozNoSzJqlC!PZGypR22j/2DD1jzuCml!eHjfkX=sT8lQYqabuOnAJ/fhI6HKdo1p0X'
                    apiUrl = 'http://nutri.larskra.de/api/v1/nutrition'

                    data = {"food":imgResponse,"grams":int(val)}

                    response = requests.post(
                                apiUrl, 
                                json = {"data":{"food":imgResponse,"grams":int(val)}},
                                headers = {"Authorization": f"Bearer {bearerTkn}" })
                    
                    print(response.json)
                    print("Post complete!")
                    cleanAndExit()                
                    # End of code #

        hx.power_down()
        hx.power_up()
        time.sleep(0.5)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
