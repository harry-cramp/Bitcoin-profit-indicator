# Author: Harry Cramp

# December 2020

import RPi.GPIO as GPIO
from time import sleep

RED_WIRE = 12
GREEN_WIRE = 18

def init():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)

	GPIO.setup(RED_WIRE, GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(GREEN_WIRE, GPIO.OUT, initial=GPIO.LOW)

def run():
	while True:
		GPIO.output(RED_WIRE, GPIO.HIGH)
		GPIO.output(GREEN_WIRE, GPIO.LOW)
		sleep(1)
		GPIO.output(RED_WIRE, GPIO.LOW)
		GPIO.output(GREEN_WIRE, GPIO.HIGH)
		sleep(1)

# when program exits, disable LEDs
def cleanup():
	GPIO.output(RED_WIRE, GPIO.LOW)
	GPIO.output(GREEN_WIRE, GPIO.LOW)

try:
	init()

	run()
finally:
	cleanup()
