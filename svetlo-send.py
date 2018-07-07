# -*- coding: utf-8 -*-

# script to send some data to Adafruit-crysma-lubo-disko LED walrus
# copyright (copyleft) crysman 2016, crysman@seznam.cz

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

# CHANGELOG:
    # 2016-12-13    * v.1.3
    #                       + command line arguments added to match svetlo-mt.py + some additional ones added
    #                       * several minor changes
    #                       * bugfix: $i incrementing properly now
    # 2016-10-29    + blinking option added #McZ
    #                       + low frequency option added  (puts some sleep in to send the data slower) #McZ
    #                       + number of total iterations and some additional statistics added and printed upon exit #McZ
    #                       + CTRL+C signal handler added #McZ
    #                       * 4 strips in total, 3 strips in three basic colors, 4th in random colors #McZ
    # 2016-xx-xx    * initial release

import time
import sys, getopt
import signal
import socket
from random import randint

#some initial constants and variables:
numpixels = 10 # number of LEDs (=90*5)
port = 6112 #network port (crysman just likes Blizzard Entertainment's games...)
ipDestination = '127.0.0.1' #'localhost'
enableBlink = False #blinking (every odd iteration brightness=0)
enableDelay = False #to have some delay between iterations
delay = 0 #how long to sleep between iterations

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


#let's handle the command line arguments:
def main(argv):
    global port
    global numpixels
    global ipDestination
    global enableBlink
    global enableDelay
    global delay

    def usage():
        sys.stderr.write("Usage:\tsvetlo-send.py [-h] [-n <numpixels>] [-p <port>] [-d <delay_in_s>] [--blink] [<IP_DESTINATION>]\n")

    try:
        opts, args = getopt.getopt(argv,"hn:p:d:",["numpixels=","port=","blink","delay="])
    except getopt.GetoptError:
        sys.stderr.write("ERR: unrecognized option, printing usage...\n")
        usage()
        sys.exit(2)
    ##print opts, args
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            usage()
            sys.exit()
        elif opt in ("--blink"):
            enableBlink = True
        elif opt in ("-d","--delay"):
            enableDelay = True
            delay =  float(arg)
            if delay < 0:
                sys.stderr.write("ERR: delay cannot be a negative number")
                sys.exit(-1)
        elif opt in ("-n", "--numpixels"):
            #must be a number:
            try:
               numpixels = int(arg)
               if (numpixels < 0):
                   sys.exit(-1)
            except:
               sys.stderr.write("ERR: numpixels must be a positive number\n")
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
    if len(args) < 2:
        if len(args) == 1:
            #this (last and only parameter without options) should be the IP address:
            ipDestination = str(args[0])
        #else: #nothing, we leave the default
    else:
        sys.stderr.write("ERR: unrecognized parameters, printing usage...\n")
        usage()
        sys.exit(2)

    usage()
    print 'Port set to: ' + str(port)
    print 'IP destination set to: ' + str(ipDestination)
    print 'Number of pixels set to: ' + str(numpixels)
    print "Delay set to: " + str(delay) + "s"
    print "Blinking enabled?: " + str(enableBlink)


#main()...
if __name__ == '__main__':
    # let's handle the command line arguments...
    main(sys.argv[1:])

    startTime = time.time()
    sendstr = ""
    strips = 4
    blinkState = False
    totalIterations = 0

    # let's prepare the networking stuff...
    print "preparing for sending data to IP " + str(ipDestination) + ', UDP port ' + str(port) + "..."
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # that is: IP, UDP
    except socket.error, msg :
        sys.stderr.write('ERR: Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit(-1)

    print "all set, starting..."
    i = 1 # we use i to determine if one strip is already full of data using modulo operation, that is why we need to start at 1 and not 0
    while True:
        signal.signal(signal.SIGINT, signal_handler)
        if enableBlink and blinkState:
            color = "0,0,0"
        else:
            if strips == 4:
                color = "0,0,255"
            elif strips == 3:
                color = "0,255,0"
            elif strips == 2:
                color = "255,0,0"
            elif strips == 1:
                #random color:
                colorR = randint(1,255)
                colorG = randint(1,255)
                colorB = randint(1,255)
                color = str(colorR) + "," + str(colorG) + "," + str(colorB)
            else:
                #this should not occur, strip0 means sending data...
                color = "255,255,255"
        ##print RGB2hex(color)
        ##print strips
        if (i % numpixels != 0):
            #we have not reached numpixels yet, so we add space between the values...
            sendstr += RGB2hex(color) + " "
        else:
            ##print "match", i
            #one strip done, put the separator in:
            sendstr += RGB2hex(color) + " |"
            strips -= 1
        if strips == 0:
            ##print sendstr, len(sendstr), i
            ##time.sleep(5)
            #the string is set-up and ready, let's go sending it:
            try:
                s.sendto(sendstr, (ipDestination, port))
            except socket.error, msg :
                sys.stderr.write('ERR: socket.sendto() failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1] + ". Is the IP address correct?\n")
                sys.exit(-1)
            #and start a new cycle:
            totalIterations += 1
            ##print "TOTALIT: ", totalIterations
            if enableDelay:
                ##print i, "sleeping for " + str(delay) + "s..."
                time.sleep(delay)
            sendstr = ""
            i = 0
            strips = 4
            blinkState = not blinkState
        ##sys.stdout.write(sendstr)
        ##sys.stdout.flush()
        i += 1

#we should never exit the loop, right?:
sys.stderr.write("WARNING: infinite loop has ended, this is not supposed to happen...")
sys.exit(-1)
