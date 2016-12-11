# -*- coding: utf-8 -*-
# script to send some data to Adafruit-crysma-lubo-disko LED walrus
# this is a multithreading version
# (copyleft) crysman 2016
# changelog:
    # 2016-10-29    * initial version based upon corresponding non-mt

import time
import sys
import signal
import socket
from random import randint
import threading

#some initial constants and setup:
NUMPIXELS = 10 # number of diods on a single strip (=90*5)
UDP_IP = "127.0.0.1"
UDP_PORT = 5004
SLEEP_INTERVAL = 0.03
ENABLE_BLINK = True #set to True if you want every second frame blank
ENABLE_LOW_FREQ = False  #set to True if you want sending data in lower frequency

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#                                     ^ Internet             ^ UDP
blinkState = False
sendstr = ""
totalIterations = 0
Strips = ["", "", "", ""]


#functions...
def signal_handler(signal, frame):
    """handling the CTRL+C"""
    totalRunTime = time.time() - startTime
    print('\nSIGINT (CTRL+C) received, exitting...')
    print("total iteratns:\t%i" % totalIterations)
    print("total runtime:\t%.2f s" % totalRunTime)
    print("--------------------------")
    print("%.1f fps" % (totalIterations/totalRunTime) )
    sys.exit(2)

def RGB2hex(string):
    """ converts an "RRR,GGG,BBB" string to hex number """
    tc = string.split(",")
    rgb_tuple = (int(tc[0]),int(tc[1]),int(tc[2]))
    ##print rgb_tuple
    hexcolor = '0x%02x%02x%02x' % rgb_tuple
    ##return int(hexcolor,16)
    return hexcolor

def fillTheStrip(name,stripIndex):
    """fills one strip with pixelcolors"""
    global Strips
#    print "--- inside the stripfill"
    for i in range(0,NUMPIXELS):
        if ENABLE_BLINK and blinkState:
            color = "0,0,0"
        else:
            if stripIndex == 0:
                color = "0,0,255"
            elif stripIndex == 1:
                color = "0,255,0"
            elif stripIndex == 2:
                color = "255,0,0"
            else:
                #random barva:
                colorR = randint(0,255)
                colorG = randint(0,255)
                colorB = randint(0,255)
                color = str(colorR) + "," + str(colorG) + "," + str(colorB)
        Strips[stripIndex] +=  RGB2hex(color) + " "
#    time.sleep(1)
#    print "//// ending stripfill" + str(stripIndex)

class myThread (threading.Thread):
    """class for multithreading [http://www.tutorialspoint.com/python/python_multithreading.htm]"""
    def __init__(self, threadID, name, stripID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.stripID = stripID
    def run(self):
        #print "Starting " + self.name
        # Get lock to synchronize threads
#        threadLock.acquire()
        fillTheStrip(self.name,self.stripID)
        # Free lock to release next thread
#        threadLock.release()


#main()...
if __name__ == '__main__':
    threadLock = threading.Lock()

    signal.signal(signal.SIGINT, signal_handler)  #handle the Ctrl+C
    startTime = time.time()
    print "blinking enabled?: " + str(ENABLE_BLINK) + " (sleep " + str(SLEEP_INTERVAL) + ")"
    print "low freq enabled?: " + str(ENABLE_LOW_FREQ)
    print "sending data on UDP port " + str(UDP_PORT) + "..."

    while True:
        #--- single thread version:

#        fillTheStrip("t0",0)
#        fillTheStrip("t1",1)
#        fillTheStrip("t2",2)
#        fillTheStrip("t3",3)

        # /// single thread

        #--- multithread version::

        thread0 = myThread(0, "Thread-0", 0)
        thread1 = myThread(1, "Thread-1", 1)
        thread2 = myThread(2, "Thread-2", 2)
        thread3 = myThread(3, "Thread-3", 3)
        # Start new Threads
        thread0.start()
        thread1.start()
        thread2.start()
        thread3.start()
        # Wait for all threads to complete
        thread0.join()
        thread1.join()
        thread2.join()
        thread3.join()

#        print "Exiting Main Thread..."
        #/// multithread

        sock.sendto(
            Strips[0] + "|" + Strips[1] + "|" + Strips[2] + "|" + Strips[3] + "|",
            (UDP_IP, UDP_PORT)
        )
#        print Strips
#        print Strips[0] + "|" + Strips[1] + "|" + Strips[2] + "|" + Strips[3] + "|"
#        print "exitting..."
#        sys.exit(-1)
        totalIterations += 1
        Strips = ["", "", "", ""]
        if ENABLE_LOW_FREQ:
            time.sleep(SLEEP_INTERVAL)
            ##print "WARNING: low freq mode enabled!"
        blinkState = not blinkState
sys.exit(0)
