#! /usr/bin/python2

from picamera import PiCamera
import time
import sys
from sendImg import sendImage

EMULATE_HX711 = False


camera = PiCamera()

referenceUnit = 449.324

sameWeight = 0

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
# hx.set_reference_unit(113)

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
        weight = hx.get_weight(5)
        print(int(weight))

        # Check if weight is not fluctuating and record the stable measurement
        if weight > 5:
            if int(weight) != int(sameWeight):
                sameWeight = weight
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

                    camera.capture('./images/image_1.jpg')
                    print("Picture Captured")
                    camera.stop_preview()

                    sendImage(weight)

                    cleanAndExit()
        # End of code #

        hx.power_down()
        hx.power_up()
        time.sleep(0.5)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
