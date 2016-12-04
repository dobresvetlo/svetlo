# -*- coding: utf-8 -*-
# script to send some data to Adafruit-crysma-lubo-disko LED walrus
# (copyleft) crysman 2016
# changelog:
    # 2016-10-29    + blinking option added
    #                       + low frequency option added  (puts some sleep in to send the data slower)
    #                       + number of total iterations and some additional statistics added and printed upon exit
    #                       + CTRL+C signal handler added
    #                       * 3 strips in three basic colors, fourth in random colors
    # 2016-xx-xx    * initial release

import time
import sys
import signal
import socket
from random import randint

#some initial constants and setup:
NUMPIXELS = 450 # počet LEDek (=90*5)
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
SLEEP_INTERVAL = 0.00001
ENABLE_BLINK = True
ENABLE_LOW_FREQ = False  #set to True if you want sending data in lower frequency


#handling the CTRL+C:
def signal_handler(signal, frame):
    totalRunTime = time.time() - startTime
    print('\nSIGINT (CTRL+C) received, exitting...')
    print("total iteratns:\t%i" % totalIterations)
    print("total runtime:\t%.2f s" % totalRunTime)
    print("--------------------------")
    print("%.1f fps" % (totalIterations/totalRunTime) )
    sys.exit(2)


#functions...
def RGB2hex(string):
    """ converts an "RRR,GGG,BBB" string to hex number """
    tc = string.split(",")
    rgb_tuple = (int(tc[0]),int(tc[1]),int(tc[2]))
    ##print rgb_tuple
    hexcolor = '0x%02x%02x%02x' % rgb_tuple
    ##return int(hexcolor,16)
    return hexcolor


#main()...
startTime = time.time()
sendstr = ""
strips = 4
blinkState = False
totalIterations = 0    

print "blinking enabled?: " + str(ENABLE_BLINK)
print "low freq enabled?: " + str(ENABLE_LOW_FREQ)
print "sending data on UDP port " + str(UDP_PORT) + "..."
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

i = 0
while True:
    signal.signal(signal.SIGINT, signal_handler)
    if ENABLE_BLINK and blinkState:
        color = "0,0,0"
    else:
        if strips == 4:
            color = "0,0,255"
        elif strips == 3:
            color = "0,255,0"
        elif strips == 2:
            color = "255,0,0"    
        elif strips == 1:
            #random barva:
            colorR = randint(0,255)
            colorG = randint(0,255)
            colorB = randint(0,255)
            color = str(colorR) + "," + str(colorG) + "," + str(colorB)
        else:
            #this should not occur, strip0 means sending data...
            color = "255,255,255"


    ##print RGB2hex(color)
    ##print strips
    if (i % NUMPIXELS != 0):
        #we have not reached NUMPIXELS yet, so we add space between the values...
        sendstr += RGB2hex(color) + " "
    else:
        #one strip done, put the separator in:
        sendstr += RGB2hex(color) + " |"
        strips -= 1
    if strips == 0:    
        ##print sendstr,i
        #the string is set-up and ready, let's go sending it:    
        sock.sendto(sendstr, (UDP_IP, UDP_PORT))
        totalIterations += 1        
        #and start a new cycle:
        sendstr = ""
        i = 0
        strips = 4
        blinkState = not blinkState
    #sys.stdout.write(sendstr)
    #sys.stdout.flush()
    i += 1
    if ENABLE_LOW_FREQ:
        time.sleep(SLEEP_INTERVAL)
exit(0)
