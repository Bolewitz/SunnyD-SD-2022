import sensor, image, pyb, time, usocket, network, sys, machine, os
from pyb import UART

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # or sensor.GRAYSCALE
sensor.set_framesize(sensor.QVGA) # or sensor.QQVGA (or others)

picture_index = [0]
uart = UART(3, 9600)
BLUE_LED_PIN = 3
GRN_LED_PIN = 2
RED_LED_PIN = 1


######## Webserver Setup #########################


def webserver(btn_exit):

    html = ''

    if btn_exit[0] == False:
        html = """ <html>
          <head>
          <form action='/action.html' method='get'>
            <title>Camera Sensor Setup</title>
            <style>
                body {
                  color: white;
                  background: #2B2C2D;
                  font-family: "Avenir", sans-serif;
                  text-shadow: 2px 2px 5px black;
                }

                h1 {
                  font-size: 35;
                  margin-bottom: -12;
                  font-style: oblique;
                  font-family: "Avenir", sans-serif;
                  color: cyan;
                  margin-top: 10;
                }

                p {
                  font-size: 20;
                  text-shadow: 2px 2px 5px black;
                  margin-top: 5;
                  margin-bottom: 10;
                  margin-left: 10;
                  color: lightgreen;
                }

                label {
                  font-size: 20;
                  text-shadow: 2px 2px 5px black;
                  cursor: default;
                  margin-top: 5;
                  margin-bottom: 5;
                  margin-left: 10;
                  display: inline-block;
                  width: 300px;
                  text-align: left;
                }

                input {
                  font-size: 15;
                  background-color: white;
                  font-weight: bold;
                  text-align: left;
                  margin-top: 5;
                  margin-bottom: 5;
                  width: 150px;
                }

                .btn {
                  width: 110px;
                  height: 50px;
                  text-align: center;
                  font-size: 18;
                  color: #393A3C;
                  background: #DADCDE;
                  border: 2px solid lightgrey;
                }

                .btn:active {
                  background: darkgrey;
                }

                img {
                  display: block;
                  margin-left: auto;
                  margin-right: auto;
                  margin-bottom: 20;
                  border: 2px solid lightgrey;
                  border-style: solid;
                }

                .cam {
                  text-align: center;
                  font-size: 20;
                  font-style: normal;
                  margin-top: 20;
                  color: cyan;
                }

                .row {
                  display: flex;
                  flex-wrap: nowrap;
                }

                .column1, .column2 {
                  flex: 50%;
                  background: #393A3C;
                  border: 2px solid lightgrey;
                }

                @media(max-width:1000px){
                  .row {
                    flex-wrap: wrap;
                  }
                  h1 {
                    text-align: center;
                  }
                  body {
                    text-align: center;
                  }
                }

            </style>
          </head>

          <h1><b>Camera Sensor Device Setup:</h1><br>
          <hr>
          <div class="row">
            <div class="column1">
              <p class="cam" >Device Parameters:</p>
              <br>
              <label for="node_id">Node ID:</label>
              <input type="text" maxlength="10" size="10" id="node_id" name="node_value" value="Node1" autofocus></input>
              <br>

              <label for="lora_id">LoRa Device Number:</label>
              <input name="lora_id" type="number" id="lora_id" min="000000000000001" max="999999999999999" value="200000000000001"></input>
              <br>

              <!--
              <label for="cap_freq">Camera Capture Frequency (Minutes):</label>
              <input name="capture_freq" max="60" size="2" min="1" type="number" id="cap_freq" value="6"></input>
              <br>
              -->

              <label for="location">Device Location (City, State):</label>
              <input name="local" text="text" id="location" size="14" value="Carolina Beach, NC">
              <br><br><br><br><br><br><br><br><br>

              <p>Device Status: OK</p>
            </div>

            <div class="column2">
              <p class="cam">Live Camera Feed</p>
              <img src="LiveFeed.jpg" alt="Live Camera Feed" width="500" height="400">

            </div>
          </div>

          <input class="btn" type="submit" name="exit_btn" value="Exit Setup">

        </form>
        </html>

         """
    else:
        html = """ <html><body>Setup Complete!</body></html> """
    return html


def wifi_Setup(SSID, KEY):
    # Init wlan module and connect to network
    print("Trying to connect... (may take a while)...")
    wlan = network.WINC()
    wlan.connect(SSID, key=KEY) # Adjust after convention (SSID, key=KEY, security=wlan.WPA_PSK)

    while(wlan.isconnected() == False):             # Initial Join for IP info
        try:
            wlan.connect(SSID, key=KEY)
            print('....')
            time.sleep(1)
        except:
            print('Error Occured.')
            time.sleep(10)      # Sleep for 10 seconds

    print("Getting IP:")

    print(wlan.ifconfig())


def start_streaming(s, btn_exit):
    print ('Waiting for connections..')
    client, addr = s.accept()
    # set client socket timeout to 2s
    client.settimeout(2.0)
    print ('Connected to ' + addr[0] + ':' + str(addr[1]))

    # Read request from client
    data = client.recv(1024)
    request = str(data)

    if (request.find('/action.html?')):             # Search for and store setup params from html GET request.
        for item in setup_param:
            dict_item = request.find(item)
            tmp_request = request[dict_item:len(request)]
            amper = tmp_request.find('&')
            setup_param[item] = tmp_request[(len(item)):amper]

    if (setup_param['node_value='] != ''):
        print('\nSetup Finished!')
        print(str(setup_param)+'\n')
        btn_exit[0] = True


    # NOTE: Disable IDE preview to increase streaming FPS.

    response = webserver(btn_exit)

    header =  "HTTP/1.1 200 OK\r\n"\
                    "Content-Type: text/html\r\n"\
                    "Connection: Close\r\n\r\n"
    client.send(header)
    client.send(response)
    # client.close()

    if (btn_exit[0] == False):
        video_streaming(s_stream, client)

    client.close()


def video_streaming(s_stream, client):
    print ('Waiting for video stream..')
    client2, addr2 = s_stream.accept()
    # set client socket timeout to 2s
    client2.settimeout(2.0)
    print ('Video Stream connected to ' + addr2[0] + ':' + str(addr2[1]))
    # Read request from client
    data = client2.recv(1024)
    # Should parse client request here

    # Send multipart header
    client2.send("HTTP/1.1 200 OK\r\n" \
                "Server: OpenMV\r\n" \
                "Content-Type: multipart/x-mixed-replace;boundary=openmv\r\n" \
                "Cache-Control: no-cache\r\n" \
                "Pragma: no-cache\r\n\r\n")

    # FPS clock
    clock = time.clock()

    # Start streaming images
    # NOTE: Disable IDE preview to increase streaming FPS.

    while (True):
        clock.tick() # Track elapsed milliseconds between snapshots()
        frame = sensor.snapshot()
        cframe = frame.compressed(quality=35)

        header = "\r\n--openmv\r\n" \
                 "Content-Type: image/jpeg\r\n"\
                 "Content-Length:"+str(cframe.size())+"\r\n\r\n"
        client2.send(header)
        client2.send(cframe)
        time.sleep(0.05)

setup_param = {"node_value=" : "",  "lora_id=" : "", "local=" : ""}      # declare dictionary to hold setup values
btn = [False]

delim = ','
csvdata = {}
lines_table = []
setup_en = False

try:
    with open('setup_data.csv', 'r') as setup_data:
        for elem in setup_data:
            lines_table.append(elem.rstrip('\n').rstrip('\r').split(delim))

    dataline = lines_table[1:2][0]  #exclude the header line

    n = 0
    for key in setup_param:
        setup_param[key] =dataline[n]
        n = n+1

    print(setup_param)

except:
    print('setup_data.csv not found, entering setup.')
    setup_en = True


if (setup_en == True):
    SSID =''     # Network SSID "OPMV_SETUP"
    KEY  =''     # Network key  "828811setup"
    HOST =''     # Use first available interface
    PORT = 80  # Arbitrary non-privileged port

    # Reset sensor
    sensor.reset()
    sensor.set_framesize(sensor.QVGA)
    sensor.set_pixformat(sensor.RGB565)

    wifi_Setup(SSID, KEY)

    # Create server socket
    s = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    s_stream = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)

    # Bind and listen
    s.bind([HOST, PORT])
    s.listen(5)

    s_stream.bind([HOST, 80])
    s_stream.listen(5)

    # Set server socket to blocking
    s.setblocking(True)
    s_stream.setblocking(True)

    while (btn[0] == False):
        try:
            start_streaming(s, btn)
        except OSError as e:
            print("socket error: ", e)
            #sys.print_exception(e)

    try:                                                                        # Write setup parameters to csv file
        with open('setup_data.csv','a') as setup_data:
            header = ','.join(str(i) for i in setup_param.keys())
            data = ','.join(str(i) for i in list(setup_param.values()))
            setup_data.write(header+'\n')
            setup_data.write(data+'\n')

    except:
        print('Error Trying to Write Setup Data File')

    print('Complete!')
    time.sleep(5)


############################################

# Timelaps Photos

# Create and init RTC object. This will allow us to set the current time for
rtc = pyb.RTC()

uart = UART(3, 9600)        # Serial for Sparrow Board

# Enable RTC interrupts every 6 minutes, camera will RESET after wakeup from deepsleep Mode.
# rtc.wakeup(360000)

while True:
    sensor.reset() # Initialize the camera sensor.
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.VGA)
    sensor.skip_frames(time = 1000) # Let new settings take affect.

    sensor.sleep(False)
    time.sleep(1)   # wait 1 second for sensor wakeup
    BLUE_LED_PIN = 3

    # Extract the date and time from the RTC object.
    dateTime = rtc.datetime()
    year = str(dateTime[0])
    month = '%02d' % dateTime[1]
    day = '%02d' % dateTime[2]
    hour = '%02d' % dateTime[4]
    minute = '%02d' % dateTime[5]
    second = '%02d' % dateTime[6]
    subSecond = str(dateTime[7])

    newName='I'+year+month+day+hour+minute+second # Image file name based on RTC

    # Let people know we are about to take a picture.
    pyb.LED(BLUE_LED_PIN).on()

    if not "images" in os.listdir(): os.mkdir("images") # Make a temp directory

    pyb.LED(BLUE_LED_PIN).off()

    # Take photo and save to SD card
    sensor.skip_frames(time = 200) # Skip some frames
    img = sensor.snapshot()
    img.save('images/' + newName, quality=90)

    uart.write(newName + '.bmp Saved to SD Card.')
    print(newName + '.bmp Saved to SD Card.')

    time.sleep(1) # wait 1 second to print

    # Enter Deepsleep Mode except for demo we are using light sleep mode to preserve serial Comms.
    sensor.sleep(True)
    time.sleep(360) # Sleep for 6 minutes (disable when using rtc interrupt)
