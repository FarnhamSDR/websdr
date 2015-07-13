import termios
#import time
import copy
import json
import serial

class Ups:
    serialPort = '' # Default in __init__()

    upsName = 'Unknown';
    upsCalibrating = False;
    upsTemp = 0.0;
    upsTrim = False;
    upsBoost = False;

    batteryVoltage = 0.0;
    batteryNominal = 0.0;
    batteryPercent = 0.0;
    batteryHealthy = True;
    batteryLow = False;

    loadVoltage = 0.0
    loadPercent = 0.0;
    loadRuntime = 0; # Minutes
    loadOk = True;

    lineVoltage = 0.0;
    lineFrequency = 0.0;
    lineOk = True;

    def __init__(self, argSerialPort='/dev/ttyS0'):
        self.serialPort = argSerialPort
        try:
            self.__openSerialPort(self.serialPort)
        except:
            return

    def dict(self):
        _dict = {}
        _dict['upsName'] = self.upsName
        _dict['upsCalibrating'] = self.upsCalibrating
        _dict['upsTemp'] = self.upsTemp
        _dict['upsTrim'] = self.upsTrim
        _dict['upsBoost'] = self.upsBoost

        _dict['batteryVoltage'] = self.batteryVoltage
        _dict['batteryPercent'] = self.batteryPercent
        _dict['batteryNominal'] = self.batteryNominal
        _dict['batteryHealthy'] = self.batteryHealthy
        _dict['batteryLow'] = self.batteryLow

        _dict['loadVoltage'] = self.loadVoltage
        _dict['loadPercent'] = self.loadPercent
        _dict['loadRuntime'] = self.loadRuntime
        _dict['loadOk'] = self.loadOk

        _dict['lineVoltage'] = self.lineVoltage
        _dict['lineFrequency'] = self.lineFrequency
        _dict['lineOk'] = self.lineOk

        return _dict

    def json(self):
        return json.dumps(self.dict())

    def refresh(self):
        self.__getUPSinfo('Y')
        self.upsName = self.__getUPSinfo('\x01')
        try:
            self.__getUPSinfo('Y')
            self.upsName = self.__getUPSinfo('\x01')
        except:
            return False

        try:
            self.batteryNominal = float(self.__getUPSinfo('g'))
            if self.batteryNominal==24.0:
                self.batteryVoltage = float(self.__getUPSinfo('B'))/2
            else:
                self.batteryVoltage = float(self.__getUPSinfo('B'))/2
            self.batteryPercent = float(self.__getUPSinfo('f'))
        except:
            return False

        try:
            self.loadPercent = float(self.__getUPSinfo('P'))
            self.loadRuntime = int(self.__getUPSinfo('j')[:-1])
        except:
            return False

        try:
            self.upsTemp = float(self.__getUPSinfo('C'))
            self.lineVoltage = float(self.__getUPSinfo('L'))
            self.lineFrequency = float(self.__getUPSinfo('F'))
            self.loadVoltage = float(self.__getUPSinfo('O'))
        except:
            return False

        try:
            statusBits = int(self.__getUPSinfo('Q'), 16)
            if statusBits & 0x01:
                self.upsCalibrating = True
            else:
                self.upsCalibrating = False

            if statusBits & 0x02:
                self.upsTrim = True
            else:
                self.upsTrim = False

            if statusBits & 0x04:
                self.upsBoost = True
            else:
                self.upsBoost = False

            if statusBits & 0x08:
                self.lineOk = True
            if statusBits & 0x10:
                self.lineOk = False

            if statusBits & 0x20:
                self.loadOk = False
            else:
                self.loadOk = True

            if statusBits & 0x40:
                self.batteryLow = True
            else:
                self.batteryLow = False

            if statusBits & 0x80:
                self.batteryHealthy = False
            else:
                self.batteryHealthy = True
        except:
            return False
        return True

    def __openSerialPort(self):
        self._fd = open(self.serialPort, 'r+', 0)
        #### Set the serial line to 2400 8n1
        #first, get the structure, so as to inherit the tty special characters
        serPortAttribs = termios.tcgetattr(self._fd)
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
        termios.tcsetattr(self._fd, termios.TCSANOW, serPortAttribs)


    def __getUPSinfo(self,sendChar):
        #       time.sleep(0.01)
        try:
            self._fd.write(sendChar)
            self._fd.flush()
            returnString1 = self._fd.readline().strip()
            # it seems like bugs in processing of the string
            # can hose up the serial port.  Prolly resolved,
            # but let's keep this just in case...
            returnString = copy.deepcopy(returnString1)
        except:
            # if the power-status changes while we're talking
            # to the serial port, it hoses up the serial port
            #  -- I think that bug got solved, but we'll keep
            # the work-around in here anyways...
            try:
                self._fd.close()
            except:
                pass
            self.__openSerialPort()
            returnString = ''
        else:
            if '!' in returnString:
                returnString = returnString.replace('!', '')
            if '$' in returnString:
                returnString = returnString.replace('$', '')
        return returnString
