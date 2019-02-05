#!/bin/bash
# a simple script to change running svetlo pattern periodically
# use `sudo nohup ./svetlochanger.sh` if you want to keep it running
# even after logout (closing ssh connection)
#
# version 2019-01-05
# crysman (copyleft) 2019

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

if [ "$(id -u)" != "0" ]; then
  echo "ERR: must be root, exitting..." >&2
  exit 1
fi
cd /home/pi/svetlo || exit 2


oldpwd="$PWD"
sleeptime=60

# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c() {
  echo "INFO: trapped CTRL-C, exitting.." >&2
  cd "$oldpwd"
  exit
}

files2play=`ls *.wlrs`
#echo $files2play

while true; do
  for newf in $files2play; do

    #do not play *.no.wlrs files:
    echo "$newf" | grep '\.no.wlrs' >/dev/null && {
      echo "INFO: skipping $newf since it contains .no in filename.." >&2
      break
    }

##    cat svetlo.ini >&2

    #set new random delay:
    digit1=$(shuf -i0-4 -n1) &&
    digit2=$(shuf -i0-9 -n1) &&
    newd="0.$digit1$digit2" &&
    #check if we've got a number:
    echo "$newd" | grep -Eq '^[-+]?[0-9]+\.?[0-9]*$' || exit 3
    sed --in-place --regexp-extended "s~delay\ ?=\ ?.*~delay = $newd~" svetlo.ini &&

    #set new brightness:
    newbr=$(shuf -i1-50 -n1) &&
    #check if we've got a number:
    echo "$newbr" | grep -Eq '^[-+]?[0-9]+\.?[0-9]*$' || exit 3
    sed --in-place --regexp-extended "s~brightness\ ?=\ ?.*~brightness = $newbr~" svetlo.ini &&

    #change .wlrs file:
    sed --in-place --regexp-extended "s~datafilename\ ?=\ ?.*~datafilename = $newf~" svetlo.ini &&

    #print new values:
    cat svetlo.ini >&2

    #restart svetlo:
    echo "OK, restarting svetlo.service .." &&
    systemctl restart svetlo.service &&

    #get some sleep:
    echo "OK, sleeping $sleeptime s .." && sleep $sleeptime
  done
done
