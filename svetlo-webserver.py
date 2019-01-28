# -*- coding: utf-8 -*-
#
# very simple webserver (using Bottle.py) to config svetlo via updating svetlo.ini file using HTML page
# notes:
#   - no or almost no at all data input validation!
#   - python2 is used due to Adafruit Dotstar limitation (does not support python3)
# crysman (copyleft) 2018-2019

# CHANGELOG:
    # 2019-01-27    * initial release: v.1.5 (v. num. synced with svetlo-mt.py)

# TODO:
# [ ] find a way how not to lose .ini comments on config.write()
# [ ] rewrite CSS to responsive design
# [ ] basic data validation
# [ ] rewrite lame atomic variables usage like boardpins1a etc. to arrays (like boardpins[])

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

#Bottle.py is licensed under MIT:
#Homepage and documentation: http://bottlepy.org/ , Copyright (c) 2009-2018, Marcel Hellkamp.


version = "1.5"

import sys, glob
import subprocess #(to be able to make system calls)
import socket #(to get ip address)

#initiate Bottle minimal web server:
#http://bottlepy.org/docs/dev/tutorial.html
from bottle import Bottle, static_file, post, request
app = Bottle()

#initiate config parser (parsing .ini files):
try:
	from configparser import ConfigParser
except ImportError:
	from ConfigParser import ConfigParser  # ver. < 3.0

sys.stderr.write("svetlo-sebserver.py version " + version + ", GPL license v3\n")

#webserver stuff:
#provide any .ico file:
@app.route('/<filename:re:.*\.ico>')
def send_static(filename):
	return static_file(filename, root='./')


#setup homepage:
@app.route('/')
def homepage():
	#get ip address by this crazy hack by https://stackoverflow.com/a/1267524:
	ipaddress = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0] or 'N/A'
	config = ConfigParser()
	config.read('svetlo.ini')
	boardpins1 = (config.get('config', 'boardpins1')).split(',')
	boardpins2 = (config.get('config', 'boardpins2')).split(',')
	boardpins3 = (config.get('config', 'boardpins3')).split(',')
	boardpins4 = (config.get('config', 'boardpins4')).split(',')
	numpixels = config.get('config', 'numpixels')
	brightness = config.get('config', 'brightness')
	port = config.get('config', 'port')
	datafilename = config.get('config', 'datafilename')
	delay = config.get('config', 'delay')

	#find available .dat files to select from:
	selectOptionsList = []
	selectOptions = ""
	if (not datafilename):
		selectOptions += '<option value="none" selected>none</option>' + '\n'
	for filename in glob.glob('*.dat'):
		selectOptionsList.append(filename)
	for filename in selectOptionsList:
		if filename == datafilename:
			selectOptions += '<option value="' + filename + '" selected>' + filename + '</option>' + '\n'
		else:
			selectOptions += '<option value="' + filename + '">' + filename + '</option>' + '\n'

	debugInfo = '<a href="https://github.com/dobresvetlo/svetlo">svetlo</a> version ' + version
	#debugInfo += str(selectOptions)

	#let's prepare the page:
	pageHTML = '''
<!doctype html>
<html lang="en">

<head>
  <title>svetlo controller</title>
  <link rel="shortcut icon" href="/favicon.ico">
  <style>
/* BASIC FORMATING - WHOLE BODY*/
.container {
	width:220px;
	border-radius: 3px;
	background-color: #f2f2f2;
	padding: 20px;
	font-family: Arial, Helvetica, sans-serif;
	font-size: 14px;
	font-weight: bold
}

.container .NA {
	color: #6D6D6D;
}

 /* INPUTS */
input, select, textarea {
	width: 200px; /* Full width */
	/*height: 40px;*/
	padding: 12px; /* Some padding */
	border: 1px solid #ccc; /* Gray border */
	border-radius: 4px; /* Rounded borders */
	box-sizing: border-box; /* Make sure that padding and width stays in place */
	margin-top: 6px; /* Add a top margin */
	margin-bottom: 6px; /* Bottom margin */
	resize: vertical /* Allow the user to vertically resize the textarea (not horizontally) */
}

/* SUBMIT BUTTON */
input[type=submit] {
	background-color: #4CAF50;
	height: 100px;
	color: white;
	padding: 5px 20px;
	border: none;
	border-radius: 4px;
	cursor: pointer;
}
input[type=submit]:hover {
	background-color: #45a049;
}

/* CANCEL BUTTON */
input[type=reset] {
	background-color: #AF814C;
	height: 50px;
	color: white;
	padding: 5px 20px;
	border: none;
	border-radius: 4px;
	cursor: pointer;
}
input[type=reset]:hover {
	background-color: #A07745;
}

.slider {
	width: 190px;
	height: 30px;
	border-radius: 3px;
	padding-left: 10px;
}

.boardpin {
	width: 60px;
	border-radius: 3px;
	padding-left: 10px;
}
  </style>
  <meta charset="UTF-8">

<script type="text/javascript">

window.onload = function() {
	if ( document.getElementById('usefile').value == 1 ) {
		document.getElementById('portsection').style.display = 'none';
	}
}

function defaultVisibility() {
	document.getElementById('portsection').style.display = 'none';
	document.getElementById('datafilenamesection').style.display = 'block';
}

function usefileHandler() {
	//alert(document.getElementById('usefile').value);
	if ( document.getElementById('usefile').value == 0 ) {
		document.getElementById('datafilenamesection').style.display = 'none';
		document.getElementById('portsection').style.display = 'block';
	} else {
		document.getElementById('datafilenamesection').style.display = 'block';
		document.getElementById('portsection').style.display = 'none';
	}
}
</script>
</head>

<body>
 <div class="container">
  <form action="/saveChanges" method="post">

	<h2>svetlo setup</h2>

	<hr>

	<label for="ip">IP Address</label><br>
	<input type="text" id="ip" name="ipaddress" value="''' + ipaddress + '''" disabled title="currently not available to modify"><br>

	<br>
	<hr>

	<label for="numpixels">Number of leds per branch</label><br>
	<input type="number" id="numpixels" name="numpixels" min="1" value="''' + numpixels + '''"><br>

	<label for="branches" class="NA">Number of branches</label><br>
	<select id="branches" name="branches" disabled title="currently not available to modify">
	  <option value="1">1</option>
	  <option value="2">2</option>
	  <option value="3">3</option>
	  <option value="4" selected>4</option>
	</select><br>

	<label for="brightness">Brightness</label><br>
	<input type="number" id="brightness" name="brightness" min="1" max="255" value="''' + brightness + '''"><br>

	<br>
	<hr>

	<label for="boardpin1a">Boardpins branch 1 (Dat, Clk)</label><br>
	<input class="boardpin" type="number" id="boardpin1a" name="boardpin1a" min="1" max="40" value="''' + boardpins1[0] + '''">
	<input class="boardpin" type="number" id="boardpin1b" name="boardpin1b" min="1" max="40" value="''' + boardpins1[1] + '''"><br>

	<label for="boardpin2a">Boardpins branch 2 (Dat, Clk)</label><br>
	<input class="boardpin" type="number" id="boardpin2a" name="boardpin2a" min="1" max="40" value="''' + boardpins2[0] + '''">
	<input class="boardpin" type="number" id="boardpin2b" name="boardpin2b" min="1" max="40" value="''' + boardpins2[1] + '''"><br>

	<label for="boardpin3a">Boardpins branch 3 (Dat, Clk)</label><br>
	<input class="boardpin" type="number" id="boardpin3a" name="boardpin3a" min="1" max="40" value="''' + boardpins3[0] + '''">
	<input class="boardpin" type="number" id="boardpin3b" name="boardpin3b" min="1" max="40" value="''' + boardpins3[1] + '''"><br>

	<label for="boardpin4a">Boardpins branch 4 (Dat, Clk)</label><br>
	<input class="boardpin" type="number" id="boardpin4a" name="boardpin4a" min="1" max="40" value="''' + boardpins4[0] + '''">
	<input class="boardpin" type="number" id="boardpin4b" name="boardpin4b" min="1" max="40" value="''' + boardpins4[1] + '''"><br>

	<br>
	<hr>

	<label for="usefile">Live input &emsp; &emsp; &emsp; &emsp; &nbsp; From file</label><br>
	<input class="slider" type="range" id="usefile" name="usefile" min="0" max="1" onchange="usefileHandler();"><br>

	<div id="datafilenamesection">
	<label for="datafilename">File to play:</label><br>
	<select id="datafilename" name="datafilename">''' + selectOptions + '''
	</select><br>
	<label for="lednewfile" class="NA">LED File Upload</label><br>
	<input type="file" id="lednewfile" name="lednewfile" accept=".dat" disabled title="currently not available"><br>
	</div>

	<div id="portsection">
	<label for="port">Port</label><br>
	<input type="number" id="port" name="port" min="1" max="65535" value="''' + port + '''"><br>
	</div>

	<label for="delay">Playback delay</label><br>
	<input type="number" id="delay" name="delay" min="0" step="0.01" value="''' + delay + '''"><br>

	<input type="submit" value="Save settings"><br>
	<input type="reset" value="Cancel" onclick="defaultVisibility();">

  </form>
</div>
<small>DEBUG: '''+ debugInfo +'''</small>
</body>
</html>
'''
	return pageHTML


#handling POST data form setup form
@app.route('/saveChanges', method='POST')
def saveChanges():
	config = ConfigParser(allow_no_value=True)
	config.read('svetlo.ini')

	boardpins1 = request.forms.get('boardpin1a')+','+request.forms.get('boardpin1b') or ''
	boardpins2 = request.forms.get('boardpin2a')+','+request.forms.get('boardpin2b') or ''
	boardpins3 = request.forms.get('boardpin3a')+','+request.forms.get('boardpin3b') or ''
	boardpins4 = request.forms.get('boardpin4a')+','+request.forms.get('boardpin4b') or ''
	numpixels = request.forms.get('numpixels') or ''
	brightness = request.forms.get('brightness') or ''
	port = request.forms.get('port') or ''
	delay = request.forms.get('delay') or ''
	usefile = request.forms.get('usefile') or ''
	if (int(usefile)):
		datafilename = request.forms.get('datafilename')
		if (datafilename == 'none'):
			datafilename = ''
	else:
		datafilename = ''

	statusText = ""
	try:
		config.set('config', 'boardpins1', boardpins1)
		config.set('config', 'boardpins2', boardpins2)
		config.set('config', 'boardpins3', boardpins3)
		config.set('config', 'boardpins4', boardpins4)
		config.set('config', 'numpixels', numpixels)
		config.set('config', 'brightness', brightness)
		config.set('config', 'port', port)
		config.set('config', 'datafilename', datafilename)
		config.set('config', 'delay', delay)
		statusText += "INFO: config values set, trying to save...<br>"
	except:
		e = sys.exc_info()[0]
		statusText = 'ERR: unable to set config values, exception details:<div>===' + str(e) + '===</div><br>'

	with open('svetlo.ini', 'w') as configfile:
		config.write(configfile)

	#restart svetlo service to run with new parameter values:
	try:
		subprocess.check_call('systemctl restart svetlo.service',shell=True)
		statusText += 'OK, svetlo.service restarted sucessfully.<br>'
	except:
		e = sys.exc_info()[0]
		statusText += 'ERR: unable to restart svetlo.service, exception details:<div>===' + str(e) + '===</div><br>'

	newHTML = '''
<!doctype html>
<html lang="en">

<head>
  <title>svetlo controller saveChanges</title>
  <link rel="shortcut icon" href="/favicon.ico">
</head>

<body>
	<p>
	input values:<br>
	bp: ''' + boardpins1 + boardpins2 + boardpins3 + boardpins4 + '''<br>
	n: ''' + numpixels + '''<br>
	b: ''' + brightness + '''<br>
	p: ''' + port + '''<br>
	f: ''' + datafilename + '''<br>
	d: ''' + delay + '''<br>
	uf: ''' + usefile + '''<br>
	<p>''' + statusText + '''
        <p>back to <a href="''' + request.headers.get('Referer') + '''">setup</a><br>
</body>
</html>
'''
	return newHTML


#run the webserver:
app.run(host='', port=80, debug=True)
