# Author: Harry Cramp

# December 2020

# PLEASE NOTE: This script uses the Alpha Vantage stocks API
# and therefore requires an API key. It is assumed to be stored in
# an environment variable called ALPHAVANTAGE_API_KEY.
# You can claim an API key here: https://www.alphavantage.co/support/#api-key

import RPi.GPIO as GPIO
import requests
import json
import datetime
import os

from time import sleep

CONFIG_SKIP_CHAR = '#'
CONFIG_CURRENCY_KEY = "currency"
CONFIG_BTC_KEY = "origin_btc_amount"
CONFIG_CASH_KEY = "origin_cash_paid"
CONFIG_RED_WIRE_KEY = "red_wire"
CONFIG_GREEN_WIRE_KEY = "green_wire"
CONFIG_START_TIME_KEY = "start_time"
CONFIG_END_TIME_KEY = "end_time"

JSON_EXCHANGE_RATE_KEY = "Exchange Rate"

ACCEPTED_NUMBER_CHARS = ".0123456789"

# delay in seconds between making API calls
CHECK_DELAY = 60

redWire = 0
greenWire = 0

start_time = 0
end_time = 0

currency = ""
originBTC = 0.0
originCash = 0.0

def get_hour():
	now = datetime.datetime.now()
	return now.hour

def get_BTC_exchange_rate():
	# fetch API key from environment variables
	api_key = os.getenv("ALPHAVANTAGE_API_KEY")
	# execute API call and get response
	response = requests.get("https://www.alphavantage.co/query?from_currency=BTC&function=CURRENCY_EXCHANGE_RATE&to_currency=" + currency + "&apikey=" + api_key)
	print("CHECKING STOCKS...")
	response_string = response.text

	# extract exchange rate from response
	noisy_data = response_string.split(JSON_EXCHANGE_RATE_KEY)[2]
	number_encountered = False
	startIndex = -1
	endIndex = -1

	for index, char in enumerate(noisy_data):
		if not number_encountered and char in ACCEPTED_NUMBER_CHARS:
			startIndex = index
			number_encountered = True
		elif number_encountered and not char in ACCEPTED_NUMBER_CHARS:
			endIndex = index
			number_encountered = False
			break

	exchange_rate = noisy_data[startIndex:endIndex]
	print("CURRENT BTC EXCHANGE RATE IN " + currency + ": " + exchange_rate)

	return float(exchange_rate)

# retrieve the value of BTC relative to the user's original investment
# i.e. if get_BTC_exchange_rate() = $20,000, originBTC = 0.5
# then get_relative_BTC_value() = $10,000 
def get_relative_BTC_value():
	exchange_rate = get_BTC_exchange_rate()
	divisor = float(1 / originBTC)
	return exchange_rate / divisor

def clear_LEDs():
	GPIO.output(redWire, GPIO.LOW)
	GPIO.output(greenWire, GPIO.LOW)

def init():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)

	# read values from config files
	config = open("config.txt", "r")
	filelines = config.readlines()

	configDict = {}
	for line in filelines:
		# skip commented lines
		if line[0] == CONFIG_SKIP_CHAR or not len(line.strip()):
			continue
		pair = line.split("=")
		configDict[pair[0]] = pair[1]

	global redWire
	global greenWire
	global originBTC
	global originCash
	global currency
	global start_time
	global end_time

	redWire = int(configDict[CONFIG_RED_WIRE_KEY])
	greenWire = int(configDict[CONFIG_GREEN_WIRE_KEY])

	originBTC = float(configDict[CONFIG_BTC_KEY])
	originCash = float(configDict[CONFIG_CASH_KEY])

	currency = configDict[CONFIG_CURRENCY_KEY].strip()

	start_time = int(configDict[CONFIG_START_TIME_KEY])
	end_time = int(configDict[CONFIG_END_TIME_KEY])

	# initialise GPIO pins
	GPIO.setup(redWire, GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(greenWire, GPIO.OUT, initial=GPIO.LOW)

def run():
	while True:
		# shut off LEDs between configured hours
		current_hour = get_hour()
		if current_hour <= start_time or current_hour >= end_time:
			clear_LEDs()
			continue

		if get_relative_BTC_value() >= originCash:
			GPIO.output(redWire, GPIO.LOW)
			GPIO.output(greenWire, GPIO.HIGH)
		else:
			GPIO.output(redWire, GPIO.HIGH)
			GPIO.output(greenWire, GPIO.LOW)

		sleep(CHECK_DELAY)

# when program exits, disable LEDs
def cleanup():
	clear_LEDs()

try:
	init()

	run()
finally:
	cleanup()
