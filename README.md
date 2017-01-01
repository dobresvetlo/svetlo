#svetlo
version 1.3

##Abstract
This is the ulti multi LED walrus crazy disco aka "svetlo"
(a project to light up some APA102 5050 LED strips using Raspberry Pi2 and Python)

(copyleft) crysman and lubo 2016


##About
_Svetlo_ means _light_ in Czech. The aim of this project is to design an open-source simplest, fastest and cheapest way to drive digital LED strips via Raspberry PI from a video source. To substitute hardware for hundreds of Euros with a cheaper one with a free and open-source code.
There are two reasons we are using STRING data format (0xffffff with a | divider) over UDP/IP:
- in the future it may be easily stored and read from a file (CSV/TXT) - to have ready-to-use "programs" available
- the Adafruit dotstar library supports similar format natively as a raw input (bytearray) - which needs to be examined further to optimize more 


##TODO/changelog
- every .py script should contain its own changelog at the beginning

###General
- [x] Demo usage video (https://youtu.be/Ho7Xqsvebsc)
- [ ] properly licence (copyleft) our python source codes and this readme (possibly GPL3?)
- [ ] Describe the usage and workflow properly in more details ("how the hack shall I use it?!")

###Coding (Python/C)
- [x] \(since v.1.3) Dynamic pixel number (how many LED diods - "pixels" - strips have got)
- [ ] Dynamic number of strips
- [ ] Add a new method (like _setStripColor_) to the Adafruit dotstar library to allow passing the whole pixel array instead of one pixel at a time (_setPixelColor_ method)
- [ ] Implementation of the OLA (Open Lighting Architecture) library to control strips via DMX512 or Artnet
- [ ] Sending raw bytearray from Touch Designer for direct input into the library (should be faster)
- [ ] Possibility to read TXT or CSV files directly as the input data and "play them"
- [ ] Test another SPI methods for filling strips
- [ ] Add TCP/IP support (currently only UDP is supported)
- [ ] Better "throttle" variables balancing/adjusting in the Adafruit dotstar library to avoid flickering

###TouchDesigner
- [ ] Variables for number of strips and pixel count
- [ ] More efficient RGB to STRING conversion
- [ ] Graphical user interface
- [ ] Implementation of recording data into TXT or CSV file and loading them

##Usage and workflow
- connect the LED strips (APA102 5050) properly and attach all to the Raspberry Pi2. Here are HOWTOs:
  - https://learn.adafruit.com/adafruit-dotstar-leds/overview
  - https://learn.adafruit.com/dotstar-pi-painter/overview (more detailed info about PINs and wiring)
- run the python script svetlo-mt.py (Rasbberry Pi2) to start the server (listening on some IP port) and process the incoming data
- run the TouchDesigner file and override the IP address accordingly to send the data
- (or optionally test with svetlo-send.py first)

##Credits:
- Project leader and enthusiast: Lubos Zbranek (sursur)
- Python coding: crysman aka #McZ
- Idea(l) contributor: Tereza Jšj

Nothing of this would have be done without the [Adafruit DotStar Pi module](https://github.com/adafruit/Adafruit_DotStar_Pi)
and [Derivative Touch Designer](http://www.derivative.ca/)
