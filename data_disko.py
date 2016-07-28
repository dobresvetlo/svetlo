#!/usr/bin/python

# Simple strand test for Adafruit Dot Star RGB LED strip.
# This is a basic diagnostic tool, NOT a graphics demo...helps confirm
# correct wiring and tests each pixel's ability to display red, green
# and blue and to forward data down the line.  By limiting the number
# and color of LEDs, it's reasonably safe to power a couple meters off
# USB.  DON'T try that with other code!

import time
import sys
from random import randint
from dotstar import Adafruit_DotStar
import numpy 
import socket

port = 5005

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", port))

#


numpixels = 10 # Number of LEDs in strip


def rgb2html(rgb_tuple):
    """ convert an (R, G, B) tuple to #RRGGBB """
    hexcolor = '#%02x%02x%02x' % rgb_tuple
    # that's it! '%02x' means zero-padded, 2-digit hex values
    return hexcolor


#for line in sys.stdin:
#    print line
#exit(3)    
    
#print rgb2html((255,000,128))
#exit(2)

# Here's how to control the strip from any two GPIO pins:
datapin   = 26
clockpin  = 19
strip     = Adafruit_DotStar(numpixels, datapin, clockpin)

# Alternate ways of declaring strip:
# strip   = Adafruit_DotStar(numpixels)           # Use SPI (pins 10=MOSI, 11=SCLK)
# strip   = Adafruit_DotStar(numpixels, 32000000) # SPI @ ~32 MHz
# strip   = Adafruit_DotStar()                    # SPI, No pixel buffer
# strip   = Adafruit_DotStar(32000000)            # 32 MHz SPI, no pixel buf
# See image-pov.py for explanation of no-pixel-buffer use.
# Append "order='gbr'" to declaration for proper colors w/older DotStar strips)

strip.begin()           # Initialize pins for output
strip.setBrightness(64) # Limit brightness to ~1/4 duty cycle

# Runs 10 LEDs at a time along strip, cycling through red, green and blue.
# This requires about 200 mA for all the 'on' pixels + 1 mA per 'off' pixel.

#1st line of data is str1 0xfe3566 0x685677 0x111111 0x678392 0x111111 0xffeef1 0xefeeff 0x111111 0xffeef1 0xefeeff

head  = 0               # Index of first 'on' pixel
tail  = -1              # Index of last 'off' pixel
color = 0xFF0000        # 'On' color (starts red)


#         GGRRBB
color = 0x0099FF
while True:
    randnum = randint(0,8)
    rand_r = randint(0,24)
    rand_g = randint(0,24)
    rand_b = randint(0,24)
    randcol = hex(rand_g)+hex(rand_r)+hex(rand_b)

    #here instead of lubosrandhex, we need to get data from udp which
    #will define the colour - non randomly

    #randhexcolor = randint(0,16581375)
    #randhexcolor = randint(0,100)
    data, addr = s.recvfrom(1024)
    #data = 'str1 0xfe3566 0x685677 0x111111 0x678392 0x111111 0xffeef1 0xefeeff 0x111111 0xffeef1 0xefeeff'
    
    randsleep = randint(1,200)
    #print("%s+%i",randcol,randhexcolor)
    #data, addr = s.recvfrom(1024)
    print data

    colour_array = []
    for i in range(0,numpixels):
        count = 5 + i*9
        #print count
        #walrus is just the dataset parsed (a single colour)
        walrus = data[count:count+6]
        #print walrus
        intwalrus = int(walrus,0)
        #print intwalrus
        colour_array.append(intwalrus)

    print colour_array

    for i in range(0,numpixels):
        #take the corresponding colour out of the colour array and assign to pixel
        KOL = colour_array[i]
        strip.setPixelColor(i, KOL)
    strip.show()
    color >>= randnum
    if(color == 0): color = 0xFF0000
    time.sleep(1.0 / 5)


exit()



while True:                              # Loop forever

	strip.setPixelColor(head, color) # Turn on 'head' pixel
	strip.setPixelColor(tail, 0)     # Turn off 'tail'
	strip.show()                     # Refresh strip
	time.sleep(1.0 / 50)             # Pause 20 milliseconds (~50 fps)

	head += 1                        # Advance head position
	if(head >= numpixels):           # Off end of strip?
		head    = 0              # Reset to start
		color >>= 8              # Red->green->blue->black
		if(color == 0): color = 0xFF0000 # If black, reset to red

	tail += 1                        # Advance tail position
	if(tail >= numpixels): tail = 0  # Off end? Reset
