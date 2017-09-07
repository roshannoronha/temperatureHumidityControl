""" 
dht22.py 
Temperature/Humidity monitor using Raspberry Pi and DHT22. 
Data is displayed at Specified google sheet
Original author: Mahesh Venkitachalam at electronut.in 
Modified by Adam Garbo on December 1, 2016 
Modified by Marcelo Paco on August 1, 2017
"""
from datetime import datetime
import sys
import RPi.GPIO as GPIO
from time import sleep
import Adafruit_DHT
from tzlocal import get_localzone
import pytz

#Google Script
from pprint import pprint
from googleapiclient import discovery
import gspread
from oauth2client.service_account import ServiceAccountCredentials

dhtsAvailable = [12, 19, 16, 13, 5, 23]
def getSensorData(number):
   RH, T = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, number)
   return (str(RH), str(T))

def main():
   print 'starting...'
   scope = ['https://www.googleapis.com/auth/spreadsheets']

   credentials = ServiceAccountCredentials.from_json_keyfile_name('DHT Monitor-aaf2f742c5ce.json', scope)
   gc = gspread.authorize(credentials)
   wks = gc.open("Temperature and Humidity").sheet1
   service = discovery.build('sheets', 'v4', credentials=credentials)

   # The ID of the spreadsheet to update.
   spreadsheet_id = '1cb4JInFFmePimsWnsNzsVI3EV_UTpRmudFtT3_BAfB4'  # TODO: Update placeholder value.
   # The A1 notation of the values to update.
   counter = 2
   range_ = 'A'+ str(counter)  # TODO: Update placeholder value.
  
   # How the input data should be interpreted.
   value_input_option = 'RAW'  # TODO: Update placeholder value.

   value_range_body = {
    	# TODO: Add desired entries to the request body. All existing entries		    	
	# will be replaced.
   }
   #Get the current time
   timeZone = pytz.timezone('America/Vancouver')
   currentDate = ' '
   currentTime = ' '
   while True:
       try:

		i = 0
                RHD1B1, TD1B1 = getSensorData(dhtsAvailable[i])
                i = i + 1
                RHD1B2, TD1B2 = getSensorData(dhtsAvailable[i])
		i = i + 1
		RHD2B1, TD2B1 = getSensorData(dhtsAvailable[i])
                i = i + 1
		RHD2B2, TD2B2 = getSensorData(dhtsAvailable[i])
		i = i + 1
                RHD3B1, TD3B1 = getSensorData(dhtsAvailable[i])
                i = i + 1
                RHD3B2, TD3B2 = getSensorData(dhtsAvailable[i])
                i = i + 1
		currentDate = datetime.now(timeZone).strftime("%d/%m/%Y")
                currentTime = datetime.now(timeZone).strftime("%I:%M:%S")
		value_range_body = {
			"values":
                        [
				[currentDate, currentTime, RHD1B1, TD1B1, RHD1B2, TD1B2, RHD2B1, TD2B1, RHD2B2, TD2B2, RHD3B1, TD3B1, RHD3B2, TD3B2]
                        ]
                }
		range_ = 'A'+ str(counter)
		request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_, valueInputOption=value_input_option, body=value_range_body)
		response = request.execute()
		counter = counter + 1
		# TODO: Change code below to process the `response` dict:
		pprint(response)
                sleep(30)
       except:
           print 'exiting.'
           break
# call main 
if __name__ == '__main__':
   main()



