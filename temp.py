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
import configparser
import asyncio
from azure.iot.device import IoTHubDeviceClient, Message
import uuid
import time



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

def writetosendcache(mssg):
	try:
		filename1 = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%fZ") 
		Path("./sendcache/").mkdir(parents=True, exist_ok=True)
		f = open('./sendcache/' + filename1, 'w')
		json.dump(mssg, f)
		f.close
	except:
		  print("An exception occurred on writing to sendcache!")

def processsendcache(devceclient):
	try:
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
			msg = Message(jsonString)
			msg.message_id = uuid.uuid4()
			msg.correlation_id = "correlation-1234"
			#msg.custom_properties["tornado-warning"] = "yes"
			devceclient.send_message(msg)
			os.remove('./sendcache/' + filename1)
	except:
		 print("An exception occurred on processing to sendcache! (" + filename1 +")")

#-------------------------------------
# Main Programm  
#-------------------------------------
def main():
	#while (1==1): 
		# Read the config

	config = configparser.ConfigParser()
	try:
		config.read('TempLogger.config')
	except:
		print("An exception occurred on reading configuration!")
		sys.exit()


	myserial = getserial()
	deviceId = 'raspi' + myserial


	IoTHubDeviceConnectionString = 'HostName=' + config['AzIoTHub']['HostName'] + ';DeviceId=' + deviceId + ';SharedAccessKey=' + config['AzIoTHubDevice']['SharedAccessKey']

	print (deviceId)

	timestamp = datetime.datetime.utcnow().isoformat()


	obj = getISSPosition() 

	jsonString = JSONEncoder().encode({
		"DeviceID": deviceId, 
		"TimestampUTC": timestamp,
		"longitude": obj['iss_position']['longitude'],
		"latitude": obj['iss_position']['latitude'],
		"cpuTemperature": str(getCpuTemperature()),
		"S1Temperature": str(getSensorTemp('28-041643c28fff')),
		"S2Temperature": str(getSensorTemp('28-031643ddf8ff')),
		"S3Temperature": str(getSensorTemp('28-0316440316ff')),
		"S4Temperature": str(getSensorTemp('28-031644338cff')),
		"S5Temperature": str(getSensorTemp('28-0316443b9eff')),
		"OperatingMinutes": str(getUptime())
	})


	# The client object is used to interact with your Azure IoT hub.
	print(IoTHubDeviceConnectionString)
	device_client = IoTHubDeviceClient.create_from_connection_string(IoTHubDeviceConnectionString)

	try:
		# Connect the client.
		device_client.connect()
		msg = Message(jsonString)
		msg.message_id = uuid.uuid4()
		msg.correlation_id = "correlation-1234"
		#msg.custom_properties["tornado-warning"] = "yes"
		device_client.send_message(msg)
	except Exception as inst:
		print("An exception occurred on sending message. (" + inst + ")")
		writetosendcache(jsonString)
	finally:
		# finally, disconnect
		try:
			device_client.disconnect()
		except Exception as e:
			print("An exception occurred disconnet device client. (" + e + ")")
		#time.sleep(5)
	
main()





