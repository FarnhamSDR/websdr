#!/usr/bin/python

serialPort = '/dev/ttyS0'
jsonPath = ''

pollTime = 30

from time import sleep
from os import system
from Ups import Ups

while(1):
    ups = Ups(serialPort)
    if not ups:
        print("Opening Serial Port failed!")
        exit()
    while not ups.refresh():
        print("UPS Poll failed, sleeping..")
        sleep(5)
    print(ups.json())
    if jsonPath!='':
        with open(jsonPath, 'w') as outfile:
            outfile.write(ups.json())
    
    if ups.batteryLow:
        if ups.refresh() and ups.batteryLow:
            system('/sbin/shutdown -h now &')
            
    sleep(pollTime)


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
