# -*- coding: utf-8 -*-

# script to receive data and light-up the Adafruit-crysma-lubo LED walrus
# this is a multi-threading version
# (copyleft) crysman 2016
# changelog:
    # 2016-12-10    * v.1.2 additional code cleanup and comments made more accurate #McZ
    #                        + getopt and command line arguments support implemented #McZ
    # 2016-12-05    * v.1.1 some code cleanup and commenting added #McZ
    # 2016-12-04    * v.1.0 debugged and working #McZ
    # 2016-11-06    * initial version based upon svetlo.py and svetlo-send-mt.py #McZ

import time
import sys, getopt
import signal
from dotstar import Adafruit_DotStar
import socket
import threading


#some initial constants and variables:
NUMPIXELS = 450 # number of LEDs (=90*5)
BRIGHTNESS = 4 # (1-255)
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 5005 # Arbitrary non-privileged port
BOARDPINS = (
# make sure that physical connections match these pins!
    (26, 19), #for the strip0
    (16, 17), #for the strip1
    (13,   6), #for the strip2
    (21, 20), #for the strip3
)

Strips = []
StripData = [
# initialize 4 empty strips:
    [],    [],    [],    [],
]
numpixels = NUMPIXELS
brightness = BRIGHTNESS
port = PORT
totalIterations = 0


#functions...
def signal_handler(signal, frame):
    """handling the CTRL+C"""
    global Strips
    totalRunTime = time.time() - startTime
    print('\nSIGINT (CTRL+C) received, exitting...')
    #let's turn it all off and let our eyes rest:
    print "setting brightness of all strips to 0..."
    for strip in Strips:
        strip.setBrightness(0)
        strip.show()
    #let's print some statistics info:
    print("total iteratns:\t%i" % totalIterations)
    print("total runtime:\t%.2f s" % totalRunTime)
    print("--------------------------")
    print("%.1f fps" % (totalIterations/totalRunTime) )
    sys.exit(2)

#def RGB2hex(string):
#    """ converts an "RRR,GGG,BBB" string to hex number """
#    tc = string.split(",")
#    rgb_tuple = (int(tc[0]),int(tc[1]),int(tc[2]))
#    ##print rgb_tuple
#    hexcolor = '0x%02x%02x%02x' % rgb_tuple
#    return int(hexcolor,16)

def fillTheStrip(name,stripIndex):
    """fills one strip with pixelcolors"""
    global Strips
    global StripData
#    print "--- inside the stripfill"
    sip = 0 #strip index pixel (one particular pixel)
    for pixelColor in StripData[stripIndex]:
        Strips[stripIndex].setPixelColor(sip,int(pixelColor,16))
        sip += 1
#    time.sleep(1)
#    print "//// ending stripfill" + str(stripIndex)

class myThread (threading.Thread):
    """class for multithreading - see [http://www.tutorialspoint.com/python/python_multithreading.htm]"""
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
        #let's shine:
        Strips[self.stripID].show()
        # Free lock to release next thread
#        threadLock.release()


#let's handle the command line arguments:
def main(argv):
    global brightness
    global port
    global numpixels
    global Strips

    def usage():
        print 'svetlo.py [-h] [-n <numpixels> [-b <brightness>] [-p <port>]'

    try:
        opts, args = getopt.getopt(argv,"h:n:b:p:",["numpixels=","brightness=","port="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            usage()
            sys.exit()
        elif opt in ("-n", "--numpixels"):
            #must be a number:
            try:
               numpixels = int(arg)
               if (numpixels < 0):
                   sys.exit(-1)
            except:
               sys.stderr.write("ERR: numpixels must be a positive number\n")
               sys.exit(-1)
        elif opt in ("-b", "--brightness"):
            #must be a number:
            try:
               brightness = int(arg)
               if (brightness > 255) or (brightness < 0):
                   sys.exit(-1)
            except:
               sys.stderr.write("ERR: brightness must be 1-255 number\n")
               sys.exit(-1)
        elif opt in ("-p", "--port"):
            #must be a number:
            try:
               port = int(arg)
               if (port < 1) or (port > 65535):
                   sys.exit(-1)
            except:
               sys.stderr.write("ERR: port must be 1-65535 number (less than 1024 is not reccommended)\n")
               sys.exit(-1)

    #strip  Adafruit_DotStar(numpixels, datapin, clockpin)
    Strips = [
        Adafruit_DotStar(numpixels, BOARDPINS[0][0], BOARDPINS[0][1]),
        Adafruit_DotStar(numpixels, BOARDPINS[1][0], BOARDPINS[1][1]),
        Adafruit_DotStar(numpixels, BOARDPINS[2][0], BOARDPINS[2][1]),
        Adafruit_DotStar(numpixels, BOARDPINS[3][0], BOARDPINS[3][1])
    ]

    usage()
    print 'Port set to: ' + str(port)
    print 'Brightness set to: ' + str(brightness)
    print 'Number of pixels set to: ' + str(numpixels)
    print 'Board PINs set to: ', BOARDPINS



#main()...
if __name__ == '__main__':
    # let's handle the command line arguments...
    main(sys.argv[1:])

    # let's prepare the networking stuff...
    # Datagram (udp) socket
    try :
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print 'Socket created, listening on UDP port ' + str(port)
    except socket.error, msg :
        sys.stderr.write('ERR: Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit(-1)
    # Bind socket to local host and port
    try:
        s.bind((HOST, port))
    except socket.error , msg:
        sys.stderr.write('ERR: Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit(-1)
    print 'Socket bind complete'

    # let's initialize all strips:
    for strip in Strips:
        strip.begin()           # Initialize pins for output
        strip.setBrightness(brightness) # set brightness
    print "all set, starting..."
    startTime = time.time()
    threadLock = threading.Lock()

    # the main infinite loop:
    while True:
        # handler for CTRL+C:
        signal.signal(signal.SIGINT, signal_handler)
        #data in this format are expected:
        #the | character separates the strips, strip data are separated by a space:
        #0xFFFFFF 0xFFFFFF ... |0xFFFFFF ... |0xFFFFFF ... |0xFFFFFF ... |
        rawdata, addr = s.recvfrom(16205) # = ((9bits * 450 LEDs) * 4 strips) = 16200 + (1bit separator * 4 strips) = 16204 bits + 1bit endline = 160205 bits
        if not rawdata:
            #we don't have any data, let's break the actual while iteration::
            sys.stderr.write("WARNING: no raw data received, breaking and waiting for next iteration...")
            break
        ##print rawdata
        ##sys.exit(-1)
        #split the incoming raw data into strips:
        StripRawData = rawdata.split("|")
        #last member is just a space character, remove it:
        del StripRawData[-1]
        #these should match:
        if len(StripRawData) != len(Strips):
            sys.stderr.write("WARNING: number of Strips does not correspond to number of stripData received...")
            break

        #let's parse the Strip data (si = strip index):
        for si in range(0,len(Strips)):
            StripData[si] = StripRawData[si].split(" ")
            #delete the last member, it's an empty string:
            del StripData[si][-1]
            if len(StripData[si]) != numpixels:
                sys.stderr.write("WARNING: StripData" + str(si) + ": #numpixels (" + str(numpixels) + ") does not correspond to number of data received (" + str(len(StripData[si]))  + ")\n")
        #Initialize threads:
        #we use Raspberry2 with 4 threads, so let's use them all:
        #myThread(int thread_id, str thread_name, int LEDstrip_id)
        thread0 = myThread(0, "Thread-0", 0)
        thread1 = myThread(1, "Thread-1", 1)
        thread2 = myThread(2, "Thread-2", 2)
        thread3 = myThread(3, "Thread-3", 3)
        #Start new Threads:
        thread0.start()
        thread1.start()
        thread2.start()
        thread3.start()
        #Wait for all threads to complete:
        thread0.join()
        thread1.join()
        thread2.join()
        thread3.join()

        ##time.sleep(1)
        ##print "----- " + str(totalIterations)
        ##print StripData

        #that is one loop done, increment the counter:
        totalIterations += 1
sys.exit(0)
