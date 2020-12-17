# Author: Harry Cramp

# December 2020

import RPi.GPIO as GPIO
from time import sleep

CONFIG_SKIP_CHAR = '#'
CONFIG_CURRENCY_KEY = "currency"
CONFIG_BTC_KEY = "origin_btc_amount"
CONFIG_CASH_KEY = "origin_cash_paid"
CONFIG_RED_WIRE_KEY = "red_wire"
CONFIG_GREEN_WIRE_KEY = "green_wire"

redWire = 0
greenWire = 0

currency = ""
originBTC = 0.0
originCash = 0.0

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

	currency = configDict[CONFIG_CURRENCY_KEY]

	# initialise GPIO pins
	GPIO.setup(redWire, GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(greenWire, GPIO.OUT, initial=GPIO.LOW)

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
