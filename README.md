# svetlo
version 1.41

## 1. Abstract
This is the ulti multi LED walrus crazy disco aka "svetlo" (a project to light up some APA102 5050 LED strips using Raspberry Pi and Python)
copyright (copyleft) _crysman #McZ_ and _lubo_ 2016-2018, GNU General Public Licence v3 ([GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html))


## 2. About
_Svetlo_ means _light_ in Czech. The aim of this project is to design an open-source simplest, fastest and cheapest way to drive digital LED strips via Raspberry PI from a video source. To substitute hardware for hundreds of Euros with a cheaper one with a free and open-source code.

## 3. Changelog
Changelog is part of every source code file in separate.

## 4. Usage, workflow, HOWTO
(info based on Raspbian Stretch 2018-04-18 running on RPi3)

### Prepare Raspberry Pi
1. Install OS Raspbian on a micro SD card:
   https://www.raspberrypi.org/documentation/installation/installing-images/
1. Insert the SD card properly into RaspberryPi ("RPi") and use it:
    1. with display, mouse and keyboard (easy), or
    1. via SSH remotely (advanced)

#### Using RPi with display, mouse and keyboard (easy)
1. Connect all peripherals
1. Plug-in the power supply and let it boot into graphical desktop environment
1. Connect to LAN via UTP cable or WiFi from the Raspbian OS desktop

#### Using RPi remotely via SSH (advanced)
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
    1. Disconnect mouse and keyboard and plug-in the power supply and let it boot. Meanwhile...
    1. ...Determine the IP address of the RPi:
       https://www.raspberrypi.org/documentation/remote-access/ip-address.md
    1. Log-in remotely into RPi using SSH from a computer:
       https://www.raspberrypi.org/documentation/remote-access/ssh/README.md
       EXAMPLE: `ssh pi@192.168.0.100` (default password is `raspberry`)
    1. [optional] Change the password (and make sure you remember it!): `passwd`

#### Configure RPi
1. Update the OS:
   ```sudo apt update && sudo apt upgrade```
1. Install git and Python:
    ```sudo apt install git python-dev python-pip```
1. Clean up a little:
   ```sudo apt autoremove && sudo apt autoclean```
1. enable SPI:
   ```sudo raspi-config``` -> Interfacing options -> enable SPI

#### Get svetlo
Go to home directory and get latest _svetlo_ from GitHub:
   ```
   cd
   git clone https://github.com/dobresvetlo/svetlo
   cd svetlo
   ```

### Prepare all the wiring and LEDs
- Connect GPIO Extension Board and LED strips (APA102 5050) and attach all properly to Raspberry Pi (see _docs and help_ folder, there are some pictures)

### Check if it works
1. Edit output pins and length of your testing APA102 strip:
   ```
   cd ~/svetlo
   nano strandtest.py
   ```
1. Light 'em up!
   ```
   sudo python ./strandtest.py
   ```
   (some LEDs should start making rainbow chase)

### Let's run it at last!
Make sure you are in svetlo directory:
```
cd ~/svetlo
```
1. Edit output pins, number of strips and their length, brightness, network port and other options:
   ```
   nano svetlo.ini
   ```
1. There are two options how to use _svetlo_ via `svetlo-mt.py`:
   1. Use it offline letting it to read data from local datafiles (default):
      ```
      sudo python svetlo-mt.py
      ```
   1. or via network using UDP:
      ```
      sudo python svetlo-mt.py --listen
      ```
      (It is now listening on default UDP port and waiting for data). Send some data:
      - Run the TouchDesigner file and override the IP address accordingly to send the data
      - (or optionally test with `svetlo-send.py` first
1. There is a simple help included, many things might be overriden from command line as arguments:
   ```
   python svetlo-mt.py --help
   ```

### Make it start automatically on (re)boot
There is a `svetlo.service` file provided to use with _systemd_ - you just need to make a symlink into _/etc/systemd..._:
```
sudo ln -s ~/svetlo/svetlo.service /etc/systemd/system/svetlo.service
```
Now test it:
- run it as system service (daemon):
  ```
  sudo systemctl start svetlo.service
  ```
- And/or stop it:
  ```
  sudo systemctl stop svetlo.service
  ```
- And/or get status:
  ```
  sudo systemctl status svetlo.service
  ```
- If you modify something in `svetlo.ini` and want to see changes, you need to restart the service:
  ```
  sudo systemctl restart svetlo.service
  ```

If everything is OK, enable the service to start on every (re)boot:
```
sudo systemctl enable svetlo.service
```

## 5. FAQ
- __Why are you using "sudo" all the time?__
The Adafruit library needs access to memory via _/dev/mem_.
- __Why string rawdata?__
There are two reasons we are using raw string data format (0xffffff with a | divider) over UDP/IP:
  - easy and readable use of datafiles to have ready-to-use "programs" available to play them in infinite loop
  - the Adafruit dotstar library supports similar format natively as a raw input (bytearray) - which needs to be examined further to optimize more
- __How to manage files on Raspberry Pi remotely?__
For copying and managing files you might use WinSCP, Filezilla, SSHFS or other options: https://www.raspberrypi.org/documentation/remote-access/
- __Where to see it in action? Some demo?__
There is an old 2016 demo usage video on YT: https://youtu.be/Ho7Xqsvebsc

## 6. Further ideas/TODO
### Coding (Python/C)
- [ ] Dynamic number of strips
- [ ] Add a new method (like _setStripColor_) to the Adafruit dotstar library to allow passing the whole pixel array instead of one pixel at a time (_setPixelColor_ method)
- [ ] Implementation of the OLA (Open Lighting Architecture) library to control strips via DMX512 or Artnet
- [ ] Sending raw bytearray from Touch Designer for direct input into the library (should be faster)
- [ ] Test another SPI methods for filling strips
- [ ] Add TCP/IP support (currently only UDP is supported)
- [ ] Better "throttle" variables balancing/adjusting in the Adafruit dotstar library to avoid flickering
- [x] Release _svetlo_ under GPLv3
- [x] Automatic start on (re)boot - might be activated via _systemd_ and included `svetlo.service` file
- [x] Change default values via configuration file (`svetlo.ini`)
- [x] Possibility to read data from files and "play them" in infinite loop while RPi is offline
- [x] Dynamic pixels number (how many LED diods - "pixels" - strips have got)

### TouchDesigner
- [ ] Variables for number of strips and pixel count
- [ ] More efficient RGB to STRING conversion
- [ ] Graphical user interface
- [ ] Implementation of recording data into file (to play them in a loop)

## 7. License
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

## 8. List of components
!TODO! UPDATE this part:
- __Raspberry PI 3B__ (depending on amount of LEDs and strips used - if not many, lower RPis might be used, too. For quad processors use multithreading version)
- __Breadboard__ (Full sized)
- __Quad Level-Shifter (3V to 5V)__ (74AHCT125 or similar, For each 2 LED strips)

## 9. Credits
- Project leader, enthusiast and hardware specialist: _Lubos Zbranek (sursur)_
- Python coding, documentation, git package: _crysman_ aka _#McZ_
- Initial idea(l) contributor: _Tereza Jšj_
- dotstar.c and dotstar.so: [Adafruit](https://github.com/adafruit/Adafruit_DotStar_Pi)

Nothing of this would have been done without the [Adafruit DotStar Pi module](https://github.com/adafruit/Adafruit_DotStar_Pi) and [Derivative Touch Designer](http://www.derivative.ca/), Thanks!
