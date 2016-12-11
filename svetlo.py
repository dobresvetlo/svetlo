# -*- coding: utf-8 -*-

# script to receive data and light-up the Adafruit-crysma-lubo LED walrus
# this is the original, single-thread version
# most comments are in Czech language, see/use the svetlo-mt.py version, it is newer, maintained and in English :)
# (copyleft) crysman 2016

import time
import sys
import signal
from dotstar import Adafruit_DotStar
import socket


#---------------------------- PINy a stripy:
#nastavení stripů a PINů:
#strip  Adafruit_DotStar(numpixels, datapin, clockpin)
NUMPIXELS = 450 # počet LEDek (=90*5)
BRIGHTNESS = 4 # svítivost (1-255)
Strips = [
        Adafruit_DotStar(NUMPIXELS, 26, 19),
        Adafruit_DotStar(NUMPIXELS, 16, 17),
        Adafruit_DotStar(NUMPIXELS, 13, 6),
        Adafruit_DotStar(NUMPIXELS, 21, 20)
    ]
for strip in Strips:
    strip.begin()           # Initialize pins for output
    #brightness jako parametr:
    if len(sys.argv) > 0:
        try: #máme vůbec nějaký parametr?
            sys.argv[1]
        except: #když ne, tak default:
            brightness = BRIGHTNESS
        else:   #když jo, šup to tam ;)
            try:
                brightness = int(sys.argv[1])
            except:
                sys.stderr.write("ERR: brightness musí být číslo 1-255\n")
                sys.exit(-1)
    strip.setBrightness(brightness) # set brightness
#//////////////////////////// /


#---------------------------- síťařina (deme poslouchat na UDP):
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 5005 # Arbitrary non-privileged port

# Datagram (udp) socket
try :
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print 'Socket created'
except socket.error, msg :
    print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit(-1)


# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error , msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit(-1)

print 'Socket bind complete'
#//////////////////////////// /


#---------------------------- pohandlujeme CTRL+C a vypneme LEDky

def signal_handler(signal, frame):
    print('\nSIGINT (CTRL+C) received, exitting...')
    #vypneme to, ať nám to nesvítí:
    for strip in Strips:
        strip.setBrightness(0)
        strip.show()
    sys.exit(2)
#//////////////////////////// /

def RGB2hex(string):
    """ converts an "RRR,GGG,BBB" string to hex number """
    tc = string.split(",")
    rgb_tuple = (int(tc[0]),int(tc[1]),int(tc[2]))
    ##print rgb_tuple
    hexcolor = '0x%02x%02x%02x' % rgb_tuple
    return int(hexcolor,16)


# --------------------------- main()
while True:
    #očekávaný formát je 6 hexahodnot oddělených mezerami + znak '|' jako oddělení stripů
    signal.signal(signal.SIGINT, signal_handler) # handler pro ukončení
    rawdata, addr = s.recvfrom(16205) # = ((9bits * 450 LEDs) * 4 strips) = 16200 + (1bit separator * 4 strips) = 16204 bits + 1bit endline = 160205 bits
    if not rawdata:
        #nemáme data, breakujeme aktuální while iteraci:
        break
    #print rawdata
    #splitneme surová data do jednotlivých stripů:
    StripRawData = rawdata.split("|")
    #poslední listmember je jen mezera, odstranit:
    del StripRawData[-1]
    #jdeme parsovat jednotlivé stripy (si = strip index):
    for si in range(0,len(Strips)):
        #splitneme surová data stripu do arraye hodnot barev:
        StripData = StripRawData[si].split(" ")
        #vymažeme posledního člena, neb to je prázdný string:
        del StripData[-1]
        ##print StripData
        sip = 0 #strip index pixel (který pixel v pásku)
        ##time.sleep(5)
        if len(StripData) != NUMPIXELS:
            sys.stderr.write("WARNING: počet NUMPIXELS neodpovídá počtu načtených sip\n")
        for pixelColor in StripData:
            ##print "%i:%i:%s" % (si,sip,pixelColor)
            Strips[si].setPixelColor(sip,int(pixelColor,16))
            ##print sip,int(pixelColor,16)
            sip += 1
        Strips[si].show()
        si += 1
    ##time.sleep(5)
exit(0) #0 = OK
