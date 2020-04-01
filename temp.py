#!/usr/bin/python3<<<<<<< HEAD
import time
import datetime
import os
import base64
import hmac
import hashlib
import requests
#import urllib2
import urllib.request
from json import JSONEncoder
from json import JSONDecoder
import json
from datetime import timedelta
from pathlib import Path

"""
Module Name:  temp.py
Project:      TempLogger
Copyright (c) Bruno Hartmann and others

Using [Send device-to-cloud message](https://msdn.microsoft.com/en-US/library/azure/mt590784.aspx) API to send device-to-cloud message from the simulated device application to IoT Hub.

This source is subject to the Microsoft Public License.
See http://www.microsoft.com/en-us/openness/licenses.aspx#MPL
All other rights reserved.

THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, 
EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.
"""
class D2CMsgSender:
    
    API_VERSION = '2016-02-03'
    TOKEN_VALID_SECS = 10
    TOKEN_FORMAT = 'SharedAccessSignature sig=%s&se=%s&skn=%s&sr=%s'
    
    def __init__(self, connectionString=None):
        if connectionString != None:
            iotHost, keyName, keyValue = [sub[sub.index('=') + 1:] for sub in connectionString.split(";")]
            self.iotHost = iotHost
            self.keyName = keyName
            self.keyValue = keyValue
            
    def _buildExpiryOn(self):
        return '%d' % (time.time() + self.TOKEN_VALID_SECS)
    
    def _buildIoTHubSasToken(self, deviceId):
        resourceUri = '%s/devices/%s' % (self.iotHost, deviceId)
        targetUri = resourceUri.lower()
        expiryTime = self._buildExpiryOn()
        toSign = '%s\n%s' % (targetUri, expiryTime)
        key = base64.b64decode(self.keyValue.encode('utf-8'))
        signature = urllib.quote(
            base64.b64encode(
                hmac.HMAC(key, toSign.encode('utf-8'), hashlib.sha256).digest()
            )
        ).replace('/', '%2F')
        return self.TOKEN_FORMAT % (signature, expiryTime, self.keyName, targetUri)
    
    def sendD2CMsg(self, deviceId, message):
        sasToken = self._buildIoTHubSasToken(deviceId)
        url = 'https://%s/devices/%s/messages/events?api-version=%s' % (self.iotHost, deviceId, self.API_VERSION)
        r = requests.post(url, headers={'Authorization': sasToken}, data=message)
        return r.status_code

# ------------------------------------------------------------------
# Read CPU Temperature
#-------------------------------------------------------------------

def getCpuTemperature():
	tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )  
	cpu_temp = tempFile.read()  
	tempFile.close()  
	return float(cpu_temp)/1000

#def getCurCpuFreq():
#	tempFile = open( "/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_cur_freq" )
#	cpu_freq = tempFile.read()
#	tempFile.close()
#	return float(cpu_freq)

# ------------------------------------------------------------------
# Extract serial from cpuinfo file
#-------------------------------------------------------------------
def getserial():
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"
 
  return cpuserial
# ------------------------------------------------------------------
# Temperatur des ersten Sensors auslesen
#-------------------------------------------------------------------
def getSensorTemp(SensorID):  
    # 1-wire Slave Datei lesen
	temperature = float('0')
	if os.path.exists('/sys/bus/w1/devices/' + SensorID + '/w1_slave'):
		file = open('/sys/bus/w1/devices/' + SensorID + '/w1_slave')
		filecontent = file.read()
		file.close()
		# Temperaturwerte auslesen und konvertieren
		stringvalue = filecontent.split("\n")[1].split(" ")[9]
		temperature = float(stringvalue[2:]) / 1000
	else:
		temperature = float('0')
		
	print('SensorID {} : Temp {}.'.format(SensorID, temperature))
	# Temperatur ausgeben
	rueckgabewert = '%6.2f' % temperature 
	return(rueckgabewert)
	
#--------------------------------------------------
#ISS Position lesen wird fuer die Positon des Raspi ---
#--------------------------------------------------
def getISSPosition():
	req = urllib.request.urlopen("http://api.open-notify.org/iss-now.json")
	response = req.read()
	print(response)
	obj = json.loads(response)
	#print obj['timestamp']
	print ('ISS Position' + obj['iss_position']['longitude'], obj['iss_position']['latitude'])
	return obj
	# Example prints:
	#   1364795862
	#   -47.36999493 151.738540034

	
def getUptime():
	with open('/proc/uptime', 'r') as f:
		uptime_minutes = float(f.readline().split()[0])//60
		#uptime_string = str(timedelta(seconds = uptime_seconds))
	print(str(uptime_minutes))
	#print(uptime_string)
	return uptime_minutes

connectionString = 'HostName=raspiiothub.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=xxx'
#deviceId = 'raspi0000000032bf4fc5'
myserial = getserial()

#device_list =[myserial,'raspi0000000032bf4fc5','raspi1000000032bf4fc5','raspi2000000032bf4fc5']
device_list =[myserial]
# Iterate over the devicelist

for deviceId in device_list:
	print (deviceId)
	#ASA - DataeTime  - String values conforming to any of ISO 8601 formats are also supported.
	#timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
	#utc_datetime = datetime.datetime.utcnow().isoformat()
	timestamp = datetime.datetime.utcnow().isoformat()
	#.strftime("%Y-%m-%d %H:%M:%S") 
	#filename = "".join(["temperaturedata", timestamp, ".log"])

	obj = getISSPosition() 

	jsonString = JSONEncoder().encode({
	  "DeviceID": deviceId, 
	  "TimestampUTC": timestamp,
	  "longitude": obj['iss_position']['longitude'],
	  "latitude": obj['iss_position']['latitude'],
	  "CpuTemperature": str(getCpuTemperature()),
	  "S1Temperature": str(getSensorTemp('28-041643c28fff')),
	  "S2Temperature": str(getSensorTemp('28-031643ddf8ff')),
	  "S3Temperature": str(getSensorTemp('28-0316440316ff')),
	  "S4Temperature": str(getSensorTemp('28-031644338cff')),
	  "S5Temperature": str(getSensorTemp('28-0316443b9eff')),
	  "OperatingMinutes": str(getUptime())
	})

	print(jsonString)
	bytes = jsonString.encode('utf-8', 'replace') 

	
	#datafile = open(filename, "w", 1)

	#message = timestamp  + "," + myserial  + "," + str(getCpuTemperature()) 
	# print message
	#d2cMsgSender = D2CMsgSender(connectionString)
	#rc = d2cMsgSender.sendD2CMsg(deviceId, bytes)
	rc=200
	# Wenn nicht erfolgreich gesendet dann in den SendCache eine Datei schreiben
	if rc != 204:
		filename1 = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%fZ") 
		Path("./sendcache/").mkdir(parents=True, exist_ok=True)
		f = open('./sendcache/' + filename1, 'w')
		json.dump(jsonString, f)
		f.close
		print('filename=' + filename1)
	print ('rc=' + str(rc))
	# Wenn  erfolgreich jetzte max 30 aus dem sendcache senden

if rc == 204:
	number = 0
	Path("./sendcache/").mkdir(parents=True, exist_ok=True)
	for filename1 in os.listdir('./sendcache/'):
		if number == 30:
			break
		number +=1
		print (filename1)
		f = open('./sendcache/' + filename1, 'r')
		x = json.load(f)
		print (x)
		bytes = x.encode('utf-8', 'replace') 
		d2cMsgSender = D2CMsgSender(connectionString)
		rc = d2cMsgSender.sendD2CMsg(deviceId, bytes)
		print (rc)
		#wenn rc nun erfolgreich dann datei loeschen
		if rc == 204:
			os.remove('./sendcache/' + filename1)
	
#count = 0
#while (count < 1000):
	#count+=1
	#Open the file with internal temp sensor
	#utc_datetime = datetime.datetime.utcnow()
	#message = utc_datetime.strftime("%Y-%m-%d %H:%M:%S")  + "," + myserial  + "," + str(getCpuTemperature()) 
	#print message
	#d2cMsgSender = D2CMsgSender(connectionString)
	#print d2cMsgSender.sendD2CMsg(deviceId, str(getCpuTemperature()))
	#time.sleep(1)

