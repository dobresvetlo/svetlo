# -*- coding: utf-8 -*-f

# svetlo - a python2 script to receive data and light-up the Adafruit-crysman-lubo LED walrus
# this is a multi-threading version
#
# copyright (copyleft) crysman #McZ 2016-2018, crysman@seznam.cz
# imported dotstar.so credit: Adafruit <https://github.com/adafruit/Adafruit_DotStar_Pi>

# LICENSE
# This file is part of svetlo.
#
# svetlo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# svetlo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with svetlo.  If not, see <https://www.gnu.org/licenses/>.

# TODO:
#   - data (colors) reproduced as BGR, not RGB (B and R swapped)
#   - add some input validation (and potencially handle it), especially:
#     line endings (CRLF vs LF), extra spaces (or newlines), ilegal characters...

# CHANGELOG:
    # 2019-01-27    * v.1.5 #McZ
    #                 * .ini format changed, specifically boardpins setup - now lowercase and separated by comma
    #                 + simple webserver added to modify conf .ini file via HTML web page
    # 2018-07-06    * v.1.41 #McZ
    #                 * released under free and open source licence GPLv3
    #                 * default UDP port set to 6112 (crysman just likes Blizzard Entertainment's games :)
    #                 + svetlo.service systemd config file provided (to be used for svetlo autostart on re/boot)
    #                 + -l (--listen) argument added to force listening on UDP instead of data from file (default)
    #                 + -f (--file) argument added to specify where to read data from
    #                 * minor bugs fixed
    # 2018-06-27    * v.1.4 #McZ
    #                 + config .ini file to read some of the variables from
    #                 + read raw data from file in loop, sample demo data included
    #                 + -d (--delay) (in sec) argument added
    #                 + version argument added
    # 2016-12-13    * v.1.3 several minor changes
    # 2016-12-10    * v.1.2 #McZ
    #                 + additional code cleanup and comments made more accurate
    #                 + getopt and command line arguments support implemented
    # 2016-12-05    * v.1.1 some code cleanup and commenting added #McZ
    # 2016-12-04    * v.1.0 debugged and working #McZ
    # 2016-11-06    * initial version based upon svetlo.py and svetlo-send-mt.py #McZ

version = "1.5"

import time
import sys, getopt
import signal
from dotstar import Adafruit_DotStar
import socket
import threading

# handle the .ini file with config and variable defaults
import ConfigParser
config = ConfigParser.ConfigParser()
config.read("svetlo.ini")
host = config.get("config", "host")
port = config.get("config", "port")
listening = False
fromfile = False
datafilename = config.get("config", "datafilename")
delay = float(config.get("config", "delay"))
brightness = int(config.get("config", "brightness"))
numpixels = int(config.get("config", "numpixels"))
#currently, only 4 strips are supported (hard-coded just here:
BOARDPINS = [
  config.get("config", "boardpins1").split(','),
  config.get("config", "boardpins2").split(','),
  config.get("config", "boardpins3").split(','),
  config.get("config", "boardpins4").split(','),
]

print BOARDPINS

Strips = []
StripData = [
# initialize 4 empty strips:
    [],    [],    [],    [],
]


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
    if (datafile):
        print("closing the opened datafile...")
        datafile.close()
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
##    print "--- inside the stripfill"
    sip = 0 #strip index pixel (one particular pixel)
    for pixelColor in StripData[stripIndex]:
        ##XXX TODO R and B are swapped :( - that is, GBR format
        colorvalue = int(pixelColor,16)
        ##print colorvalue
        Strips[stripIndex].setPixelColor(sip,colorvalue)
        sip += 1
##    time.sleep(1)
##    print "//// ending stripfill" + str(stripIndex)

class myThread (threading.Thread):
    """class for multithreading - see <http://www.tutorialspoint.com/python/python_multithreading.htm>"""
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
    global listening
    global fromfile
    global datafilename
    global port
    global numpixels
    global delay
    global Strips
    global version

    def usage():
        print("svetlo-mt.py version " + version + ", GPL license v3")
        print("Usage: svetlo-mt.py [-h] [-V] [-n <numpixels>] [-d <delay (in s)>] [-b <brightness>] [-l] [-p <port>] [-f <filename>]")

    try:
        opts, args = getopt.getopt(sys.argv[1:],"n:d:b:p:f:lhV",["numpixels=","delay=","brightness=","port=","file=","listen","help","version"])
    except getopt.GetoptError:
        sys.stderr.write("ERR: unrecognized option, printing usage...\n")
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            sys.stderr.write("printing help...\n")
            usage()
            sys.exit()
        elif opt in ('-V', "--version"):
            sys.stderr.write("svetlo multithread version " + version + "\n")
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
        elif opt in ("-d", "--delay"):
            #must be a number:
            try:
               delay = float(arg)
               if (delay < 0):
                   sys.exit(-1)
            except:
               sys.stderr.write("ERR: delay must be a positive float number\n")
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
        elif opt in ("-l", "--listen"):
            #force to operate in networking mode (listen on UDP port):
            listening = True
        elif opt in ("-f", "--filename"):
            fromfile = True
            datafilename = str(arg)
        elif opt in ("-p", "--port"):
            #must be a number:
            try:
               port = int(arg)
               if (port < 1) or (port > 65535):
                   sys.exit(-1)
            except:
               sys.stderr.write("ERR: port must be 1-65535 number (less than 1024 is not reccommended)\n")
               sys.exit(-1)
        else:
            sys.stderr.write("ERR: unrecognized option, printing usage...\n")
            usage()
            sys.exit(2)

    #strip  Adafruit_DotStar(numpixels, datapin, clockpin)
    Strips = [
        Adafruit_DotStar(int(numpixels), int(BOARDPINS[0][0]), int(BOARDPINS[0][1])),
        Adafruit_DotStar(int(numpixels), int(BOARDPINS[1][0]), int(BOARDPINS[1][1])),
        Adafruit_DotStar(int(numpixels), int(BOARDPINS[2][0]), int(BOARDPINS[2][1])),
        Adafruit_DotStar(int(numpixels), int(BOARDPINS[3][0]), int(BOARDPINS[3][1]))
    ]

    usage()
    if (listening):
        print 'listening mode enabled (port must be set!)'
    if (fromfile and not listening):
        print 'Reading data from: ' + str(datafilename)
    if (port and not fromfile):
        print 'Port set to: ' + str(port)
    else:
        print 'Port not set, expecting to read data from file...'
    print 'Brightness set to: ' + str(brightness)
    print 'Number of pixels set to: ' + str(numpixels)
    print 'Delay set to: ' + str(delay)
    print 'Board PINs set to: ', BOARDPINS


totalIterations = 0
datafile = ''

#main()...
if __name__ == '__main__':
    # let's handle the command line arguments...
    main(sys.argv[1:])

    #how many B are we going to read?:
    ##bytestoread = 16205 # = ((9bits * 450 LEDs) * 4 strips) = 16200 + (1bit separator * 4 strips) = 16204 bits + 1bit endline = 160205 bits
    bytestoread = 9*numpixels*4+1*4+1

    #where to read data from?:
    if(datafilename and not listening):
        #read data from file:
        try:
            print 'Datafile specified, trying to read from ' + str(datafilename) + "..."
            datafile = open(datafilename, "r")
        except:
            sys.stderr.write("WARNING: could not open the file " + datafilename + ", switching to network mode...\n")
            datafile = False
    ##print datafile.read()
    ##exit(-1)
    if (not datafile):
        # let's prepare the networking stuff...
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # that is: IP, UDP
        except socket.error, msg :
            sys.stderr.write('ERR: Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit(-1)
        # Bind socket to local host and port
        try:
            if (port):
                s.bind((host, int(port)))
            else:
                sys.stderr.write('ERR: neither port or datafile specified, no data to read from\n')
                sys.exit(-1)
            print 'Socket created and bound, listening on UDP port ' + str(port) + "..."
        except socket.error , msg:
            sys.stderr.write('ERR: Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit(-1)

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
        # handler for SIGTERM (used e.g. by systemd):
        signal.signal(signal.SIGTERM, signal_handler)
        #data in this format are expected:
        #the | character separates the strips, strip data (paarticular LEDs) are separated by a space:
        #0xFFFFFF 0xFFFFFF ... |0xFFFFFF ... |0xFFFFFF ... |0xFFFFFF ... |
        if (datafile):
            #read data from file:
            #(expecting UNIX endlines  (LF))
            rawdata = datafile.read(bytestoread)
        else:
            #read data from network:
            rawdata, addr = s.recvfrom(bytestoread)
        ##print datafile.tell()
        if not rawdata:
            #we don't have any data, let's break the actual while iteration and continue:
            ##sys.stderr.write("WARNING: no raw data received, breaking and waiting for next iteration...\n")
            #reset the file pointer to the beginning of the file again:
            if (datafile):
                datafile.seek(0,0)
            #break the loop with continue:
            continue
        ##print rawdata
        ##sys.exit(-1)
        #split the incoming raw data into strips:
        StripRawData = rawdata.split("|")
        #last member is just a space character, remove it:
        del StripRawData[-1]
        #these should match:
        if len(StripRawData) != len(Strips):
            sys.stderr.write("WARNING: number of Strips does not correspond to number of stripData received...\n")
            break

        #let's parse the Strip data (si = strip index):
        for si in range(0,len(Strips)):
            StripData[si] = StripRawData[si].split(" ")
            #delete the last member, it's an empty string:
            del StripData[si][-1]
            if len(StripData[si]) != numpixels:
                sys.stderr.write("WARNING: StripData" + str(si) + ": #numpixels (" + str(numpixels) + ") does not correspond to number of data received (" + str(len(StripData[si]))  + ")\n")
                print StripData[si]
                ##sys.stderr.write("sleeping 10s...")
                ##time.sleep(10)
                ##sys.stderr.write("done sleeping.")

        #Initialize threads:
        #we use Raspberry3 with 4 threads, so let's use them all:
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

        if (delay):
            ##print "sleeping <delay>s..."
            time.sleep(delay)
        ##print "----- " + str(totalIterations)
        ##print StripData

        #that is one loop done, increment the counter:
        totalIterations += 1
##        if (datafile):
##            print datafile.tell()


#we should never exit the loop, right?:
sys.stderr.write("WARNING: oops! infinite loop has ended, this is not supposed to happen...\n")
sys.exit(-1)
