# Basic Image Capture Code
# Captures image every 6 minutes and saves using an index number to the SD card

import sensor, image, pyb, time

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # or sensor.GRAYSCALE
sensor.set_framesize(sensor.QVGA) # or sensor.QQVGA (or others)
sensor.skip_frames(time = 2000) # Let new settings take affect.

sensor.skip_frames(time = 2000) # Give the user time to get ready.

picture_index = [0]

while(True):
    sensor.snapshot().save(str(picture_index[0]) + ".jpg")   # Save as index #
    print("Image " + str(picture_index[0]) + " Saved.")    # Print saved image info

    picture_index[0] += 1

    time.sleep(360)   # Wait 6 minutes
