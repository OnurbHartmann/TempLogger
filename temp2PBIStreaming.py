"""
Python sample for Raspberry Pi which reads temperature and humidity values from
a DHT22 sensor, and sends that data to Power BI for use in a streaming dataset.
"""

import urllib, urllib2, time
from datetime import datetime
#import Adafruit_DHT as dht

# type of sensor that we're using
#SENSOR = dht.DHT22 	

# pin which reads the temperature and humidity from sensor
#PIN = 4			

# REST API endpoint, given to you when you create an API streaming dataset
# Will be of the format: https://api.powerbi.com/beta/<tenant id>/datasets/< dataset id>/rows?key=<key id>
REST_API_URL = "https://api.powerbi.com/beta/155f9b14-4627-4424-8868-c6b96023c639/datasets/6abbe1f5-f171-4a8f-978d-60201aea2561/rows?key=mtRzYZJBNbfjSxN3EpjUPgkBF2FvlwszSE%2BRKAHFRnyHmFSIO2etucYr22%2FZzlP3Nk3kNah%2BMyqdtFY%2Bj1v1QA%3D%3D"

"""  JSON as Follows
[{
 "TimeStampUTC" :"2016-12-26T18:56:23.135Z",
 "CpuTemperature" :"AAAAA555555"
}]
"""
# ------------------------ Function -----------------------------
def getCpuTemperature():
	tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )  
	cpu_temp = tempFile.read()  
	tempFile.close()  
	return float(cpu_temp)/1000


# Gather temperature and sensor data and push to Power BI REST API
while True:
	try:
		# read and print out humidity and temperature from sensor
		temp = getCpuTemperature()
		print 'Temp={0:0.1f}*C'.format(temp)
		
		# ensure that timestamp string is formatted properly
		now = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S%Z")
		nowUTC= datetime.strftime(datetime.utcnow(), "%Y-%m-%dT%H:%M:%S%Z")
		# data that we're sending to Power BI REST API
		data = '[{{ "TimeStampUTC": "{0}", "CpuTemperature": "{1:0.1f}"}}]'.format(now, temp)
	
		# make HTTP POST request to Power BI REST API
		req = urllib2.Request(REST_API_URL, data)
		response = urllib2.urlopen(req)
		print("POST request to Power BI with data:{0}".format(data))
		print("Response: HTTP {0} {1}\n".format(response.getcode(), response.read()))	
	
		time.sleep(1)
	except urllib2.HTTPError as e:
		print("HTTP Error: {0} - {1}".format(e.code, e.reason))
	except urllib2.URLError as e:
		print("URL Error: {0}".format(e.reason))
	except Exception as e:
		print("General Exception: {0}".format(e))

