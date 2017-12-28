import RPi.GPIO as GPIO
import os
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
KILLSWITCH = 18
GPIO.setup(KILLSWITCH, GPIO.IN)

def killswitch():
	print(GPIO.input(KILLSWITCH))
	#if GPIO.input(KILLSWITCH) != GPIO.HIGH:
		#os.system("sudo shutdown -h now")

def main():
	while True:
		killswitch()
		time.sleep(0.2)

if __name__ == "__main__":
	main()
