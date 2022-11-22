import sensor, image, pyb, time, usocket, network, sys, tf
from pyb import UART

picture_index = [0]
uart = UART(3, 9600)
BLUE_LED_PIN = 3

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # or sensor.GRAYSCALE
sensor.set_framesize(sensor.QVGA) # Special 128x160 framesize for LCD Shield.
sensor.skip_frames(time = 2000)

# Load model
net = tf.load('betamodel5.tflite', load_to_fb = True)

clock = time.clock()

while(True):
    clock.tick()

    sensor.sleep(False) # exit sleep
    pyb.LED(BLUE_LED_PIN).on()
    sensor.skip_frames(time = 500) # Let new settings take affect.
    pyb.LED(BLUE_LED_PIN).off()

    sensor.snapshot().save(str(picture_index[0]) + ".jpg")   # Save as index #
    print("Image " + str(picture_index[0]) + " Saved.")    # Print saved image info

    img = sensor.snapshot()
    infer_objects = net.classify(img)
    print("flooded vs not flooded" + str(infer_objects))

    print(clock.fps())

    uart.write('Image '+str(picture_index[0])+' Printed')

    picture_index[0] += 1
    #sensor.sleep(True) # Enter Sleep
    #time.sleep(360) # Sleep for 6 minutes

