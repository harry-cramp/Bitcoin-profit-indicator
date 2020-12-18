# Author: Harry Cramp

# December 2020

# PLEASE NOTE: This script uses the Alpha Vantage stocks API
# and therefore requires an API key. It is assumed to be stored in
# an environment variable called ALPHAVANTAGE_API_KEY.
# You can claim an API key here: https://www.alphavantage.co/support/#api-key

import RPi.GPIO as GPIO
import requests
import json
import os

from time import sleep

CONFIG_SKIP_CHAR = '#'
CONFIG_CURRENCY_KEY = "currency"
CONFIG_BTC_KEY = "origin_btc_amount"
CONFIG_CASH_KEY = "origin_cash_paid"
CONFIG_RED_WIRE_KEY = "red_wire"
CONFIG_GREEN_WIRE_KEY = "green_wire"

JSON_EXCHANGE_RATE_KEY = "Exchange Rate"

ACCEPTED_NUMBER_CHARS = ".0123456789"

redWire = 0
greenWire = 0

currency = ""
originBTC = 0.0
originCash = 0.0

def get_BTC_exchange_rate():
	# fetch API key from environment variables
	api_key = os.getenv("ALPHAVANTAGE_API_KEY")
	# execute API call and get response
	response = requests.get("https://www.alphavantage.co/query?from_currency=BTC&function=CURRENCY_EXCHANGE_RATE&to_currency=" + currency + "&apikey=" + api_key)
	response_string = response.text
	print(response_string)

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

	return noisy_data[startIndex:endIndex]

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
		print("LINE: " + line)
		pair = line.split("=")
		configDict[pair[0]] = pair[1]

	global redWire
	global greenWire
	global originBTC
	global originCash
	global currency

	redWire = int(configDict[CONFIG_RED_WIRE_KEY])
	greenWire = int(configDict[CONFIG_GREEN_WIRE_KEY])

	originBTC = float(configDict[CONFIG_BTC_KEY])
	originCash = float(configDict[CONFIG_CASH_KEY])

	currency = configDict[CONFIG_CURRENCY_KEY].strip()

	# initialise GPIO pins
	GPIO.setup(redWire, GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(greenWire, GPIO.OUT, initial=GPIO.LOW)

	print(get_BTC_exchange_rate())

def run():
	while True:
		GPIO.output(redWire, GPIO.HIGH)
		GPIO.output(greenWire, GPIO.LOW)
		sleep(1)
		GPIO.output(redWire, GPIO.LOW)
		GPIO.output(greenWire, GPIO.HIGH)
		sleep(1)

# when program exits, disable LEDs
def cleanup():
	GPIO.output(redWire, GPIO.LOW)
	GPIO.output(greenWire, GPIO.LOW)

try:
	init()

	run()
finally:
	cleanup()
