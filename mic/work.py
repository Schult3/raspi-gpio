import time
import RPi.GPIO as GPIO
import sound_analysis as sa
import killswitch as k

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
LED1 = 11
GPIO.setup(LED1, GPIO.OUT)


pwm1 = GPIO.PWM(LED1, 100)
pwm1.start(0)

def main():
	while True:
		k.killswitch()
		power = sa.getSoundPWM()
		if power > 50:
			pwm1.ChangeDutyCycle(power)
			power_amp = power
		else:
			power_amp -= 5
			if power_amp <= 20:
				power_amp = 20
			pwm1.ChangeDutyCycle(power_amp)

if __name__ == '__main__':
	main()
