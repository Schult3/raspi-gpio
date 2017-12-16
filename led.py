import time
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
# RPi.GPIO Layout verwenden (wie Pin-Nummern)
GPIO.setmode(GPIO.BOARD)

LED = 11
# Pin 11 (GPIO 17) auf Output setzen
GPIO.setup(LED, GPIO.OUT)

pwm = GPIO.PWM(LED, 100)
pwm.start(0)
power = 20

# Dauersschleife
while 1:
	if power >= 100:
		power = 0

	pwm.ChangeDutyCycle(power)  
  	time.sleep(0.1)
	power += 1
