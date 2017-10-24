"""
Program: 	Cooper's Pi Alarm - The Software
Version: 	0.0.2
Author:		JoshuaCooper
"""
#Setup
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

#SetupVars
armed = True
bttn = 25
loginTries = 0

#RGBLED
redLed = 14
greenLed = 15
blueLed = 18

#GPIOsetup
GPIO.setup(redLed,GPIO.OUT) # Sets Red to be an output
GPIO.setup(greenLed,GPIO.OUT) # Sets Green to be an output
GPIO.setup(blueLed,GPIO.OUT) # Sets Blue to be output
GPIO.setup(bttn, GPIO.IN, pull_up_down = GPIO.PUD_UP) #Sets the button, as if it was in a pull up.

#Allthecodes
mainPIN = 1234
adminPIN = 4321

def disarm():
	global armed, bttn, loginTries, redLed, greenLed, blueLed, mainPIN, adminPIN
	lockedOut = False
	while armed == True:
		if lockedOut == False:
			# When first ran, set LEDs to Red.
			GPIO.output(redLed, True)
			GPIO.output(greenLed, False)
			GPIO.output(blueLed, False)
			
			# Then ask for PIN.
			enteredPIN = int(input("To disarm, enter pin: "))
			
			if enteredPIN == mainPIN: # If they enter the disarm pin...
				armed = False # Then disarm the alarm...
				print("DISARMED") # Say it's disarmed...
				GPIO.output(redLed, False) 
				GPIO.output(greenLed, True) # Then set LED to green.
				GPIO.output(blueLed, False)
				arming()

			elif enteredPIN == adminPIN: # But if they enter the admin pin....
				armed = False # Still disarm the alarm...
				print("IT Mode") # But say IT MODE...
				GPIO.output(redLed, False) 
				GPIO.output(greenLed, False)
				GPIO.output(blueLed, True) # Turn the LED blue...
				time.sleep(50) # and wait 50s

			else:
				armed = True # Else just keep it armed...
				print("ARMED")
				enteredPIN = ""
				GPIO.output(redLed, True) # And sets the leds to red.
				GPIO.output(greenLed, False)
				GPIO.output(blueLed, False)
				loginTries += 1
				if loginTries >= 4:
					print("Locked Out")
					lockedOut = True
				else:
					print("Try again!")
		else:
			problem()

			
def arming():
	global armed, bttn, loginTries, redLed, greenLed, blueLed, mainPIN, adminPIN
	while armed == False:
		# When first ran, set LEDs to Green.
		GPIO.output(redLed, False)
		GPIO.output(greenLed, True)
		GPIO.output(blueLed, False)
		
		# Then ask for PIN.
		enteredPIN = int(input("To arm, enter pin: "))
		if enteredPIN == mainPIN:
			print("ARMING")
			armed = True
			disarm()
			
		else:
			armed = False # Else just keep it disarmed...
			print("still DISARMED, Please try again!")
			enteredPIN = ""
			GPIO.output(redLed, False) # And sets the leds to GREEN.
			GPIO.output(greenLed, True)
			GPIO.output(blueLed, False)
			
def motion1():
	global armed, bttn, mainPIN
	while armed == True:
		detect1 = GPIO.input(bttn)
		if detect1 == 0:
			disarm()
				
def arming():
		global mainPIN, armed, redLed, greenLed, blueLed
		# Then ask for PIN.
		enteredPIN = int(input("To arm, enter pin: "))
		time.sleep(10)
		if enteredPIN == mainPIN:
			print("ARMING")
			armed = True
			disarm()
			
		else:
			armed = False # Else just keep it disarmed...
			print("still DISARMED, Please try again!")
			enteredPIN = ""
			GPIO.output(redLed, False) # And sets the leds to GREEN.
			GPIO.output(greenLed, True)
			GPIO.output(blueLed, False)
			
def problem():
	global armed, redLed, greenLed, blueLed
	while armed == True:
		GPIO.output(redLed, True)
		GPIO.output(greenLed, False)
		GPIO.output(blueLed, False)
		time.sleep(1)
		GPIO.output(redLed, False)
		GPIO.output(greenLed, False)
		GPIO.output(blueLed, True)
		GPIO.output(blueLed, True)
		time.sleep(1)

try:
	if armed == True:
		motion1()

	
finally:
	print("\n\nHousekeeping!\n")
	GPIO.cleanup()

