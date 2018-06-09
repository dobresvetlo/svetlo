# RaspberryPi setup and usage (HOWTO)
(info based on Raspbian Stretch 2018-04-18 running on RPi3)

1. Install OS Raspbian on a micro SD card:
   https://www.raspberrypi.org/documentation/installation/installing-images/
1. Insert the SD card properly into RaspberryPi ("RPi") and use it:
    1. with display, mouse and keyboard (easy), or
    1. via SSH remotely (advanced)

## Using RPi with display, mouse and keyboard (easy)
1. Connect all peripherals
1. Plug-in the power supply and let it boot into graphical desktop environment
1. Connect to LAN via UTP cable or WiFi from the Raspbian OS desktop

## Using RPi remotely via SSH (advanced)
1. Allow SSH connections on RPi:
    1. Make an empty file named `ssh` in the root of the boot partition of the RPi SD card:
       https://www.raspberrypi.org/documentation/remote-access/ssh/README.md
    1. Connect RPi to LAN:
       1. via UTP cable (no setup needed), or
       1. via Wi-Fi: edit the file `/etc/wpa_supplicant/wpa_supplicant.conf` on the RPi SD card's system partition and replace the content of it with this:
       ```
       ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
       update_config=1
       network={
    	   ssid="YOUR_NETWORK_SSID"
    	   psk="YOUR_NETWORK_PASSWORD"
    	   scan_ssid=1
       }
       ```       
		1. Disconnect all peripherals and plug-in the power supply and let it boot. Meanwhile...
    1. ...Determine the IP address of the RPi:
       https://www.raspberrypi.org/documentation/remote-access/ip-address.md
    1. Log-in remotely into RPi using SSH from a computer:
       https://www.raspberrypi.org/documentation/remote-access/ssh/README.md
       EXAMPLE: `ssh pi@192.168.0.100` (default password is `raspberry`)
    1. Change the password (and make sure you remember it): `passwd`

## Configuring RPi
1. Update the OS:
   ```sudo apt update && sudo apt upgrade```
1. Install git and Python:
	```sudo apt install git python-dev python-pip```
1. Clean up a little:
   ```sudo apt autoremove && sudo apt autoclean```
1. enable SPI:
   ```sudo raspi-config``` -> Interfacing options -> enable SPI
1. Set-up DOBRE SVETLO:
   ```
   cd
   git clone https://github.com/dobresvetlo/svetlo
   cd svetlo
   ```

## Managing files remotely
For copying and managing files you might use WinSCP, Filezilla, SSHFS or other options:
https://www.raspberrypi.org/documentation/remote-access/

## Connect GPIO Extension Board and LED strips
...
TODO
...

## Test LED strips
1. Edit output pins and length of your testing APA102 strip:
   ```
   cd ~/svetlo
   nano strandtest.py
   ```
1. Light 'em up!
   ```
   sudo python ./strandtest.py
   ```
   (LEDs should start making rainbow chase)

## DOBRE SVETLO
1. Edit output pins, number of strips and their length:
   ```
   cd ~/svetlo  
   nano svetlo.py
   ```
1. Run DOBRE SVETLO:
   ```
   sudo python ~/.svetlo.py
   ```
   (it is waiting for data now...)
1. Feed it with data!:
   1. Use one of the included `svetlo-send.py` scripts, or:
   1. Run TouchDesigner to send some data and update output IP and pixelcount matching Raspberry's
1. BLINK! :)


## List of components
!TODO! UPDATE this part: 
- Raspberry PI 3B 
	(Depends on amount of LEDs and strips used - for Quad processors could be used multithreading code)
- Breadboard (Full sized)
- Quad Level-Shifter (3V to 5V) (74AHCT125 or similar, For each 2 LED strips
