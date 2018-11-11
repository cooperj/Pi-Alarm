"""
Program: 	Cooper's Pi Alarm - The Software
Version: 	2.1
Author:		Joshua Cooper
Last Edit:	17-APR-18
----
Big thanks to Matt Hawkins at Raspberry Pi Spy for the LCD screen example code!
"""

#Setup
import RPi.GPIO as GPIO
import time
from twilio.rest import Client
from threading import Thread
import configparser
from datetime import datetime
import threading
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, Future
import os
import smbus

GPIO.setmode(GPIO.BCM) #Set GPIO to be in BCM mode

#Config Syncing
config = configparser.ConfigParser()
config.read('config.ini')
#---Open Config Data as Variables---
accountSid = config['sms']['accountSid']
authToken = config['sms']['authToken']
myTwilioNum = config['sms']['myTwilioNum']
myMobileNum = config['sms']['myMobileNum']
problemMsg = config['messages']['problemMsg']

#SMS Settings
client = Client(accountSid, authToken)

#--SetupVars--
armed = True
loginTries = 0
backlight = True
arm_length = 15

#GPIO vars
bttn1 = 26
bttn2 = 19
bttn3 = 6

pir1 = 23
beeper = 18
siren = 17

redled = 8
greenled = 15
yellowled = 25

GPIO.setup(siren,GPIO.OUT) # Sets siren to be an output
GPIO.setup(beeper, GPIO.OUT)
GPIO.setup(redled,GPIO.OUT) # Sets Red to be an output
GPIO.setup(greenled,GPIO.OUT) # Sets Green to be an output
GPIO.setup(yellowled,GPIO.OUT) # Sets Blue to be output
GPIO.setup(pir1, GPIO.IN)
# Set button's as inputs
GPIO.setup(bttn1, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(bttn2, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(bttn3, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)


#==LCD CODE==
# Define some device parameters
I2C_ADDR	= 0x27 # I2C device address
LCD_WIDTH = 16	 # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT = 0x08 # Backlight on

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)	# Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

#////ALARM PROGRAM STARTS HERE////

def lcd_init():
	# Initialise display
	lcd_byte(0x33,LCD_CMD) # 110011 Initialise
	lcd_byte(0x32,LCD_CMD) # 110010 Initialise
	lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
	lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
	lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
	lcd_byte(0x01,LCD_CMD) # 000001 Clear display
	time.sleep(E_DELAY)

def lcd_byte(bits, mode):
	# Send byte to data pins
	# bits = the data
	# mode = 1 for data
	#				0 for command

	bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
	bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

	# High bits
	bus.write_byte(I2C_ADDR, bits_high)
	lcd_toggle_enable(bits_high)

	# Low bits
	bus.write_byte(I2C_ADDR, bits_low)
	lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
	# Toggle enable
	time.sleep(E_DELAY)
	bus.write_byte(I2C_ADDR, (bits | ENABLE))
	time.sleep(E_PULSE)
	bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
	time.sleep(E_DELAY)
	
def lcd_string(message,line):
	# Send string to display

	message = message.ljust(LCD_WIDTH," ")

	lcd_byte(line, LCD_CMD)

	for i in range(LCD_WIDTH):
		lcd_byte(ord(message[i]),LCD_CHR)

def backlightcontrol():
	global LCD_BACKLIGHT, backlight
	if backlight == True:
		LCD_BACKLIGHT = 0x08 # Backlight on
	elif backlight == False:
		LCD_BACKLIGHT = 0x00 # Backlight off

def panic():
	global siren, yellowled, bttn1
	t = 0
	while t != 1200:
		t += 1
		bttn1Pressed = GPIO.input(bttn1)
		if bttn1Pressed == 1:
			GPIO.output(siren, False)
			GPIO.output(yellowled, True)
		else:
			GPIO.output(yellowled, True)
			GPIO.output(siren, True)
			time.sleep(1)

	GPIO.output(siren, False)
	time.sleep(1)
	#while bttn1Pressed != 1:
		#bttn1Pressed = GPIO.input(bttn1)

	#print("escaped panic")

def arm():
	global arm_length, beeper, armed
	armed = True
	GPIO.output(greenled, False)
	arm_count = 0
	
	while arm_count < arm_length:
		arm_str = str(arm_length - arm_count)
		arm_count += 1
		lcd_string("Please Leave...",LCD_LINE_1)
		lcd_string("Arming in "+ arm_str +"s",LCD_LINE_2)
		GPIO.output(redled, True)
		GPIO.output(beeper, True)
		time.sleep(0.1)
		GPIO.output(beeper, False)
		GPIO.output(redled, False)
		time.sleep(1)
	
	lcd_string("COOPER RPI-ALARM",LCD_LINE_1)
	lcd_string("     ARMED!",LCD_LINE_2)
	GPIO.output(redled, True)
	GPIO.output(beeper, True)
	time.sleep(0.5)
	GPIO.output(beeper, False)
	
def disarm():
	global beeper, armed
	armed = False
	GPIO.output(redled, False)
	GPIO.output(greenled, True)
	lcd_string("COOPER RPI-ALARM",LCD_LINE_1)
	lcd_string("    DISARMED",LCD_LINE_2)
	GPIO.output(beeper, True)
	time.sleep(0.5)
	GPIO.output(beeper, False)

def bttnInput():
	#print("bttnInput")
	global bttn1, bttn2, bttn3
	while True:
		GPIO.output(yellowled, False)
		GPIO.output(beeper, False)
		
		bttn1Pressed = GPIO.input(bttn1)
		bttn2Pressed = GPIO.input(bttn2)
		bttn3Pressed = GPIO.input(bttn3)

		if bttn3Pressed == 1: # The RED button
			problem()
			
		elif bttn2Pressed == 1: # The TRIANGLE button
			arm()
			
		elif bttn1Pressed == 1: # The CIRCLE button
			disarm()
		
		
def problem():
	global myTwilioNum, myMobileNum, problemMsg, client
	lcd_string("PROBLEM, TO STOP",LCD_LINE_1)
	lcd_string("  Hold Disarm!",LCD_LINE_2)
	theTime = str(datetime.now().strftime(" on %d %B at %H:%M"))
	client.messages.create(from_=myTwilioNum,
						to=myMobileNum,
						body=problemMsg + theTime,)
	timer_timeout = 0
	panic()

def pir():
	global armed, pir1
	while armed == True:
		GPIO.input(pir1)
		if pin1 == 1:
			panic()
		else:
			time.sleep(0.2)
	
try:
	GPIO.output(siren, True)
	lcd_init()
	lcd_string("COOPER RPI-ALARM",LCD_LINE_1)
	lcd_string("VERISON: 2.0",LCD_LINE_2) # Announce software version
	#print("ALARM SYSTEM STARTING!")
	time.sleep(5)
	lcd_string("COOPER RPI-ALARM",LCD_LINE_1)
	lcd_string("     ARMED!",LCD_LINE_2)	
	GPIO.output(redled, True)
	GPIO.output(siren, False)
	pool = ThreadPoolExecutor(max_workers=2)
	while True:
		bttnInput = pool.submit(bttnInput)
		pir = pool.submit(pir)

	
finally:
	#print("\n\n/////Bye For Now/////")
	lcd_string("GOODBYE FOR NOW!",LCD_LINE_1)
	lcd_string("see you later...",LCD_LINE_2)
	GPIO.cleanup()
	#print("\n(･‿･)ﾉ\n")
