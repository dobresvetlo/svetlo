# svetlo
##Abstract
This is the ulti multi LED walrus crazy disco aka "svetlo"
(a project to light up some APA102 5050 LED strips using Raspberry Pi2 and Python)

(copyleft) crysman and lubo 2016


##About
_Svetlo_ means _light_ in Czech. The aim of this project is to design an open-source simplest, fastest and cheapest way to drive digital LED strips via Raspberry PI from a video source. To subtitute hardware for hundreds of Euros with a cheaper one with an open-source code.
There are two reasons we are using STRING FORMAT (0xffffff with a | divider) of data over UDP/IP:
- in the future it could be easily stored and read from a file (e.g. CSV)
- the Adafruit C library supports similar format natively as a raw input (bytearray) 


##TODO and changelog
###Python
- [x] Dynamic pixel number
- [ ] Describe the usage and workflow properly in more details ("how the hack shall I use it?!")
- [ ] Dynamic number of strips
- [ ] Add a method to the Adafruit library to allow submitting the whole array of pixels instead of one pixel at a time
- [ ] Implementation of the OLA (Open Lighting Architecture) library to control strips via DMX512 or Artnet
- [ ] Sending raw bytearray from Touch Designer for direct input into the library (should be faster)
- [ ] Possibility to read TXT or CSV files directly as the input data and "play them"
- [ ] Test another SPI methods for filling the strips
- [ ] Add TCP/IP support (currently only UDP is supported)
- [ ] Better balancing of the "throttle" variables in the Adafruit library to avoid flickering

###TouchDesigner
- [ ] Variables for number of strips and pixel count
- [ ] More efficient RGB to STRING conversion
- [ ] Graphical user interface
- [ ] Implementation of recording data into TXT or CSV file and loading them

##Usage and workflow
- connect the LED strips (APA102 5050) properly and attach all to the Raspberry Pi2 - see the [Adafruit tutorial here](https://learn.adafruit.com/adafruit-dotstar-leds/overview/)
- run the python script svetlo-mt.py (Rasbberry Pi2) to listen and process the incoming data
- run the TouchDesigner file and override the IP address accordingly to send the data
- (or optionally test with svetlo-send.py first)

##Credits:
- Project leader and enthusiast: Lubos Zbranek (sursur)
- Python coding: crysman aka #McZ
- Idea(l) contributor: Tereza Jšj

Nothing of this would be done without the [Adafruit DotStar Pi module](https://github.com/adafruit/Adafruit_DotStar_Pi)
and [Derivative Touch Designer](http://www.derivative.ca/)
