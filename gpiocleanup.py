"""
Project:	GPIOcleanup
Author: 	Joshua Cooper
Version:	1.0
"""
import RPi.GPIO as GPIO
var = 0

print("\nStarting Clean up!")

while var != 10:
	print(var)
	var += 1

GPIO.cleanup()

print("\nCleaned up!\nNow Closing!")