# -*- coding: utf-8 -*-
# script to receive data to Adafruit-crysma-lubo-disko LED walrus
# this is a multithreading version
# (copyleft) crysman 2016
# changelog:
    # 2016-12-04    * v.1.0 debugged and working
    # 2016-11-06    * initial version based upon disko01.py and disko-send-mt.py

import time
import sys
import signal
from dotstar import Adafruit_DotStar
import socket
import threading


#some initial constants and setup:
#strip  Adafruit_DotStar(numpixels, datapin, clockpin)
NUMPIXELS = 450 # počet LEDek (=90*5)
BRIGHTNESS = 4 # svítivost (1-255)
Strips = [
        Adafruit_DotStar(NUMPIXELS, 26, 19),
        Adafruit_DotStar(NUMPIXELS, 16, 17),
        Adafruit_DotStar(NUMPIXELS, 13, 6),
        Adafruit_DotStar(NUMPIXELS, 21, 20)
    ]
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 5005 # Arbitrary non-privileged port
totalIterations = 0    
StripData = [
    [],    [],    [],    []
]


#functions...
def signal_handler(signal, frame):
    global Strips
    """handling the CTRL+C"""
    totalRunTime = time.time() - startTime
    print('\nSIGINT (CTRL+C) received, exitting...')
    #let's turn it all off and let our eyes rest:
    print "setting brightness of all strips to 0..."
    for strip in Strips:
        strip.setBrightness(0)
        strip.show()    
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
    return int(hexcolor,16)

def fillTheStrip(name,stripIndex):
    """fills one strip with pixelcolors"""
    global Strips
    global StripData
#    print "--- inside the stripfill"
    sip = 0 #strip index pixel (který pixel v pásku)
    for pixelColor in StripData[stripIndex]:
        ##fillTheStrip(str(si),si,pixelColor,sip)
        Strips[stripIndex].setPixelColor(sip,int(pixelColor,16))
        sip += 1    
    
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
        #tak si to zobrazíme:
        Strips[self.stripID].show()        
        # Free lock to release next thread
#        threadLock.release()

#main()...
if __name__ == '__main__':
    # let's handle the command line arguments...
    #brightness as an argument:
    if len(sys.argv) > 0:
        try: #do we actrually have any argument?
            sys.argv[1]
        except: #if not, set to default:
            brightness = BRIGHTNESS
        else:   #if yes, use it:
            try:
                brightness = int(sys.argv[1])
            except:
                sys.stderr.write("ERR: brightness must be 1-255 number\n")
                sys.exit(-1)
           
    # let's prepare the networking stuff...
    # Datagram (udp) socket
    try :
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print 'Socket created, listening on port ' + str(PORT)
    except socket.error, msg :
        sys.stderr.write('ERR: Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit(-1)    
     # Bind socket to local host and port
    try:
        s.bind((HOST, PORT))
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
    
    while True:
        #očekávaný formát je 6 hexahodnot oddělených mezerami + znak '|' jako oddělení stripů
        signal.signal(signal.SIGINT, signal_handler) # handler pro ukončení
        rawdata, addr = s.recvfrom(16208) # = ((9bitů * 450 diod) * 4 stripy) + (2 bity oddělovač * 4 stripy)
        if not rawdata:
            #nemáme data, breakujeme aktuální while iteraci:
            sys.stderr.write("WARNING: no raw data received, breaking and waiting for next iteration...")    
            break
        #print rawdata
        #splitneme surová data do jednotlivých stripů:
        StripRawData = rawdata.split("|")
        #poslední listmember je jen mezera, odstranit:
        del StripRawData[-1]
        #pokud počet stripDat neodpovídá počtu stripů, máme problém...
        if len(StripRawData) != len(Strips):
            sys.stderr.write("WARNING: number of Strips does not correspond to number of stripData received...")
            break    
        
        #jdeme parsovat jednotlivé stripy (si = strip index):
        for si in range(0,len(Strips)):            
            StripData[si] = StripRawData[si].split(" ")        
            #vymažeme posledního člena, neb to je prázdný string:
            del StripData[si][-1]
            if len(StripData[si]) != NUMPIXELS:
                sys.stderr.write("WARNING: StripData" + str(si) + ": počet NUMPIXELS neodpovídá počtu načtených sip\n")  

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

        ##time.sleep(1)
        ##print "----- " + str(totalIterations)            
        totalIterations += 1
exit(0) #0 = OK
