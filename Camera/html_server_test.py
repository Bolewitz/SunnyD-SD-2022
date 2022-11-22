import sensor, image, time, network, usocket, sys

def webserver():

    frame = sensor.snapshot()
    cframe = frame.compressed(quality=35)
    html = ''

    if btn_exit == False:
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
              <br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>

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

def wifi_Setup():
    # Init wlan module and connect to network
    print("Trying to connect... (may take a while)...")
    wlan = network.WINC()
    wlan.connect(SSID, key=KEY, security=wlan.WPA_PSK)

    while(wlan.isconnected() == False):             # Initial Join for IP info
        try:
            wlan.connect(SSID, key=KEY, security=wlan.WPA_PSK)
            print('....')
            time.sleep(1)
        except:
            print('Error Occured.')

    print("Getting IP:")

    wlan_conn_tup = wlan.ifconfig()
    wlan_ls = (list(wlan_conn_tup))
    wlan_ip = (list(wlan_ls[0]))
    wlan_ip[len(wlan_ip)-2] = '0'
    wlan_ip[len(wlan_ip)-1] = '8'

    wlan_ls[0] = ''.join(wlan_ip)
    wlan_conn_tup = tuple(wlan_ls)
    wlan.ifconfig((wlan_conn_tup))

    wlan.disconnect()       # disconnect and connect again with the new static IP

    while(wlan.isconnected() == False):             # Final Join

        try:
            wlan.connect(SSID, key=KEY, security=wlan.WPA_PSK)
            print('....')
            time.sleep(1)
        except:
            print('Error Occured.')

    print(wlan.ifconfig())


setup_param = {"node_value=" : "",  "lora_id=" : "", "local=" : ""}      # declare dictionary to hold setup values
btn_exit = False

SSID ='SpectrumSetup-C7'     # Network SSID "OPMV_SETUP"
KEY  ='legalstudio631'     # Network key  "828811setup"
HOST =''     # Use first available interface
PORT = 80  # Arbitrary non-privileged port

# Reset sensor
sensor.reset()
sensor.set_framesize(sensor.QVGA)
sensor.set_pixformat(sensor.RGB565)

wifi_Setup()

# Create server socket
s = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
s_stream = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)

# Bind and listen
s.bind([HOST, PORT])
s.listen(5)

s_stream.bind([HOST, 5000])
s_stream.listen(5)

# Set server socket to blocking
s.setblocking(True)
s_stream.setblocking(True)

def start_streaming(s):
    print ('Waiting for connections..')
    client, addr = s.accept()
    # set client socket timeout to 2s
    client.settimeout(2.0)
    print ('Connected to ' + addr[0] + ':' + str(addr[1]))

    # Read request from client
    data = client.recv(1024)
    request = str(data)

    print(request)

    if (request.find('/action.html?')):             # Search for and store setup params from html GET request.
        for item in setup_param:
            dict_item = request.find(item)
            tmp_request = request[dict_item:len(request)]
            amper = tmp_request.find('&')
            setup_param[item] = tmp_request[(len(item)):amper]

        print(setup_param)

    # Should parse client request here
    # FPS clock
    clock = time.clock()

    # NOTE: Disable IDE preview to increase streaming FPS.

    clock.tick() # Track elapsed milliseconds between snapshots().
   # frame = sensor.snapshot()
    #cframe = frame.compressed(quality=35)


    response = webserver()

    header =  "HTTP/1.1 200 OK\r\n"\
                    "Content-Type: text/html\r\n"\
                   "Connection: close\r\n\r\n"
    client.send(header)
    client.send(response)
    client.close()


def video_streaming(s_stream):
    print ('Waiting for connections..')
    client2, addr2 = s_stream.accept()
    # set client socket timeout to 2s
    client2.settimeout(2.0)
    print ('Connected to ' + addr2[0] + ':' + str(addr2[1]))
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
        clock.tick() # Track elapsed milliseconds between snapshots().
        frame = sensor.snapshot()
        cframe = frame.compressed(quality=35)

        header = "\r\n--openmv\r\n" \
                 "Content-Type: image/jpeg\r\n"\
                 "Content-Length:"+str(cframe.size())+"\r\n\r\n"
        client2.send(header)
        client2.send(cframe)
        time.sleep(0.05)

while True:
    while (btn_exit == False):
        try:
            start_streaming(s)
            video_streaming(s_stream)
        except OSError as e:
            print("socket error: ", e)
            #sys.print_exception(e)
