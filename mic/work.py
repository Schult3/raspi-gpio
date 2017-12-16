import time
import RPi.GPIO as GPIO
import sound_analysis as sa
import killswitch as k

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
LED1 = 11
LED2 = 13
LED3 = 15
GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)
GPIO.setup(LED3, GPIO.OUT)

pwm1 = GPIO.PWM(LED1, 1000)
pwm1.start(0)

pwm2 = GPIO.PWM(LED2, 1000)
pwm2.start(0)

pwm3 = GPIO.PWM(LED3, 1000)
pwm3.start(0)

def main():
	power_amp = 0

	while True:
		#k.killswitch()
		power = sa.getSoundPWM()
		if power >= 75:
			pwm3.ChangeDutyCycle(power)
			pwm2.ChangeDutyCycle(100)
			pwm1.ChangeDutyCycle(100)
		elif power >= 50:
			pwm2.ChangeDutyCycle(power)
			pwm3.ChangeDutyCycle(0)
			pwm1.ChangeDutyCycle(100)
		elif power >= 20:
			pwm1.ChangeDutyCycle(power)
			pwm2.ChangeDutyCycle(0)
			pwm3.ChangeDutyCycle(0)
			power_amp = power
		else:
			power_amp -= 5
			if power_amp <= 20:
				power_amp = 20
			pwm1.ChangeDutyCycle(power_amp)
			pwm2.ChangeDutyCycle(0)
			pwm3.ChangeDutyCycle(0)

if __name__ == '__main__':
	main()
