#!/usr/bin/python
#
#
# Talks to Smart-UPSes and shuts-down as needed.  Also syslogs a
# regular status report
#
# fassler at cira dot colostate dawt eeh deeh you
#
# Based on excellent notes on the smart-UPS protocol at 
#   http://www.apcupsd.com/manual/ch29s04.html and
#   http://www.wsrcc.com/wolfgang/ups/
#
#######################################
#
# Instructions:  
#
# 1. Edit the next few variables to your liking
#
# 2. Edit sendShutdown() and cancelShutdown() to your liking
#
# 3. Copy this to, say, /usr/local/sbin/
#
# 4. Add this to your /etc/inittab, with a line like this:
#       ups:12345:respawn:/usr/local/sbin/smartUPSd.py
#
# 5. Reload init with "init q"
#
#

# what serial port is the Smart-UPS connected to
serialPort = '/dev/ttyS0'

# about how many seconds in between status reports 
# (in your syslog) under normal conditions
normalPollTime = 3600

# about how many seconds in between status reports 
# when power has failed
failurePollTime = 15

# about how many seconds does a power failure (or power 
# restore) have to last before we believe it
patience = 30 

# 1 for syslog, 0 for stdout
useSyslog = 1

# put your shutdown and cancel shutdown commands here
def sendShutdown():
	sendMessage("Sending shutdown command")
	myCommand = '/sbin/shutdown -h +5 "        ******  Power failure  ******"&'
	#os.system(myCommand)
	
def cancelShutdown():
	sendMessage("Cancelling shutdown...")
	myCommand = '/sbin/shutdown -c "*** Power restored, shutdown cancelled ***"'
	#os.system(myCommand)


################################################
# You prolly shouldn't have to change anything past this point


import select
import sys
import os
import termios
import time
import syslog
import copy


if useSyslog:
	syslog.openlog("smartUPSd")

def sendMessage(myString):
	if useSyslog:
		syslog.syslog(myString)
	else:
		print myString

def declarePowerFailure():
	global powerGood
	global timeout
	global failTime
	sendMessage(" *** Power outage")
	if powerGood:
		powerGood = 0
		timeout = failurePollTime
		failTime = time.time()

def declarePowerRestored():
	global powerGood
	global timeout
	global restoreTime
	sendMessage(" *** Power Restored")
	if not powerGood:
		powerGood = 1
		restoreTime = time.time()
	if not shuttingDown:
		timeout=normalPollTime

def getUPSinfo(sendChar):
	global fd
#	the protocol docs say you shouldn't talk to the UPS too
# 	fast, but I haven't noticed any problems...
#	time.sleep(0.01)
	try:
		fd.write(sendChar)
		fd.flush()
		returnString1 = fd.readline().strip()
		# it seems like bugs in processing of the string
		# can hose up the serial port.  Prolly resolved,
		# but let's keep this just in case...
		returnString = copy.deepcopy(returnString1)
	except:
		# if the power-status changes while we're talking
		# to the serial port, it hoses up the serial port
		#  -- I think that bug got solved, but we'll keep
		# the work-around in here anyways...
		sendMessage("problem on serial port: "+ sendChar)
		sendMessage(str(sys.exc_type))
		sendMessage("Attempting to reopen the serial port")
		try:
			fd.close()
		except:
			pass
		fd = openSerialPort()
		returnString = ''
	else:
		if '!' in returnString:
			declarePowerFailure()
			returnString = returnString.replace('!', '')
		if '$' in returnString:
			declarePowerRestored()
			returnString = returnString.replace('$', '')
	return returnString

def secondsToFormat(seconds):
	# all integer math
	seconds = int(seconds)
	days = seconds/ 86400
	seconds = seconds % 86400
	hours = seconds / 3600
	seconds = seconds % 3600
	minutes = seconds/ 60
	seconds = seconds % 60
	daPieces = []
	if days:
		if days == 1:
			daPieces.append("1 day")
		else:
			daPieces.append(str(days) + " days")
	if hours:
		if hours == 1:
			daPieces.append("1 hour")
		else:
			daPieces.append(str(hours) + " hours")
	if minutes:
		if minutes == 1:
			daPieces.append("1 minute")
		else:
			daPieces.append(str(minutes) + " minutes")
	if seconds:
		if seconds == 1:
			daPieces.append("1 second")
		else:
			daPieces.append(str(seconds) + " seconds")
	if not daPieces:
		daPieces = ['0 seconds']
	return ', '.join(daPieces)

def getStatus():
	try:
		getUPSinfo('Y')
		modelName = getUPSinfo('\x01')
	except:
		sendMessage("getUPSinfo() failed")
	else:
		sendMessage("")
		sendMessage( "     " + modelName + "  on " + serialPort)
		sendMessage("")
	try:
		battVoltage = getUPSinfo('B')
		nominalBattVoltage = str(int(getUPSinfo('g')))
		battPercent = str(int(float(getUPSinfo('f'))))
	except:
		sendMessage("getUPSinfo() failed")
	else:
		sendMessage( "Battery: %s volts (%s%%).  (%s volts nominal)" % \
			(battVoltage, battPercent, nominalBattVoltage))
		# what the hell does "nominal battery voltage" mean anyway?...
	try:
		lastBatteryChange = getUPSinfo('x')
	except:
		sendMessage("getUPSinfo() failed")
	else:
		sendMessage( "Battery was last replaced on " + lastBatteryChange)
	try:
		powerLoad = str(float(getUPSinfo('P')))
		estRuntime = str(int(getUPSinfo('j')[:-1]))
	except:
		sendMessage("getUPSinfo() failed")
	else:
		sendMessage( "Power load: %s%%,  estimated runtime: %s minutes" % (powerLoad, estRuntime))

	try:
		internalTemp = str(float(getUPSinfo('C')))
		lineVoltage = str(float(getUPSinfo('L')))
		lineFreq = getUPSinfo('F')
		outVoltage = getUPSinfo('O')
	except:
		sendMessage("getUPSinfo() failed")
	else:
		sendMessage( "Internal Temp: %s C,  Line: %s volts @ %s Hz.  Out: %s volts" % \
			(internalTemp, lineVoltage, lineFreq, outVoltage))
	try:
		statusBits = int(getUPSinfo('Q'), 16)
	except:
		sendMessage("getUPSinfo() failed")
	else:
		sendMessage("statusBits: 0x%02.x:" % (statusBits))
		if statusBits & 0x01:
			sendMessage("     - Runtime calibration")
		if statusBits & 0x02:
			sendMessage("     - SmartTrim")
		if statusBits & 0x04:
			sendMessage("     - SmartBoots")
		if statusBits & 0x08:
			sendMessage("     - UPS is online")
			if not powerGood:
				declarePowerRestored()
		if statusBits & 0x10:
			sendMessage("     - UPS is on battery")
			if powerGood:
				declarePowerFailure()
		if statusBits & 0x20:
			sendMessage("     *** Too much load on UPS!")
		if statusBits & 0x40:
			sendMessage("     - Battery is low")
		if statusBits & 0x80:
			sendMessage("     *** Replace battery!")
		sendMessage("")
	if powerGood:
		powerGoodTime = time.time() - restoreTime
		sendMessage("Power has been good for " + secondsToFormat(powerGoodTime))
	else:
		powerBadTime = time.time() - failTime
		sendMessage("Power has been out for " + secondsToFormat(powerBadTime))

def openSerialPort():
	fd = open(serialPort, 'r+', 0)
	#### Set the serial line to 2400 8n1
	#first, get the structure, so as to inherit the tty special characters
	serPortAttribs = termios.tcgetattr(fd)
	#iflag
	serPortAttribs[0] = termios.IGNBRK
	#oflag
	serPortAttribs[1] = 0x0
	#cflag - ignore CTS/RTS | enable receiver | 2400 |   8n1  (n and 1 are 0x0)
	serPortAttribs[2] = termios.CLOCAL | termios.CREAD | termios.B2400 | termios.CS8
	#lflag
	serPortAttribs[3] = 0x0
	#ispeed
	serPortAttribs[4] = termios.B2400
	#ospeed
	serPortAttribs[5] = termios.B2400
	# Do the dastardly deed
	termios.tcsetattr(fd, termios.TCSANOW, serPortAttribs)
	return fd

fd = openSerialPort()

timeout = normalPollTime
powerGood = 1
shuttingDown = 0
restoreTime = time.time()
getStatus()

while(1):
	inputs, outputs, errors = select.select([fd], [], [], timeout)
	if inputs:
		myChar = fd.read(1)
		if myChar == '!':
			declarePowerFailure()
		elif myChar == '$':
			declarePowerRestored()
	elif not powerGood and not shuttingDown:
		if time.time() - failTime > patience:
			sendShutdown()
			shuttingDown = 1
		getStatus()
	elif powerGood and shuttingDown:
		if time.time() - restoreTime > patience:
			cancelShutdown()
			shuttingDown = 0
			timeout=normalPollTime
		getStatus()
	else:
		getStatus()

