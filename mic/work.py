rr# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import time
import sound_analysis as sa
from neopixel import *
import argparse
import signal
import sys
import json
import random
import os.path

def signal_handler(signal, frame):
        colorWipe(strip, Color(0,0,0))
        sys.exit(0)

def opt_parse():
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', action='store_true', help='clear the display on exit')
        args = parser.parse_args()
        if args.c:
                signal.signal(signal.SIGINT, signal_handler)

# LED strip configuration:
LED_COUNT      = 134      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering


FLG_CHANGE_COLOR = 0
AKT_MODUS = ""

# Equalizer Einstellungen
HIST_AMP = 0
POS_OFFSET = []

# Tetris Einstellungen
TET_QUEUE_POS = 0 #Position des Stapels
TET_QUEUE_NEG = LED_COUNT - 1
TET_LAUFNUMMER = LED_COUNT - 1 #Aktuelle Position des Elements
TET_RICHTUNG = 1

#RunningLights config
RL_CARS = []

#Chrystal config
CH_TWINKLE = []

#Rainbow config
RB_J = 0

#RunningCircle config
RC_LIST = []
RC_RICHTUNG = 0

#While Loop config
FLG_CHANGE_EFFECT = 0
EFFECT_COUNTER = 1

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def initialize(strip, color, wait_ms=10):
	x = strip.numPixels() / 2
	for i in range(x):
		strip.setPixelColor(i, color)
		strip.setPixelColor(strip.numPixels() - i - 1, color)
		strip.show()
		time.sleep(wait_ms / 1000.0)
	time.sleep(wait_ms / 1000.0)

def destroy(strip, color, wait_ms=10):
	x = strip.numPixels() / 2
	while x >= 0:
		strip.setPixelColor(x, color)
		strip.setPixelColor(strip.numPixels() - x - 1, color)
		strip.show()
		time.sleep(wait_ms / 1000.0)
		x -= 1


def rainbow(strip, color):
    global AKT_MODUS
    global RB_J
    global FLG_CHANGE_EFFECT

    if AKT_MODUS != "RB":
        RB_J = 0
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))

    for i in range(256):
        strip.setPixelColor(i, wheel((i + RB_J) & 255))

    RB_J += 1

    if RB_J >= 256:
        FLG_CHANGE_EFFECT = 1
        RB_J = 0

    strip.show()
    AKT_MODUS = "RB"

def equalizer(strip, color, parts=4):
	global HIST_AMP
	global POS_OFFSET

	amp = sa.getSoundPWM()
	max_pixels = strip.numPixels() / parts
	anz_pixels = amp / 100.0 * max_pixels
	anz_pixels = round(anz_pixels, 0)

	if len(POS_OFFSET) != parts:
		for i in range(parts):
			POS_OFFSET.append(i * max_pixels)

	hist_anz_pixels = HIST_AMP / 100.0 * max_pixels
	hist_anz_pixels = round(hist_anz_pixels, 0)
	if amp > HIST_AMP:
		i = int(hist_anz_pixels)
		while i <= anz_pixels:
			for x in POS_OFFSET:
				strip.setPixelColor(x + i, wheel(x + i))
			strip.show()
			i += 1
	else:
		i = int(hist_anz_pixels)
		while i >= anz_pixels:
			for x in POS_OFFSET:
				strip.setPixelColor(x + i, Color(0, 0, 0))
			strip.show()
			i -= 1

	HIST_AMP = amp


def strobe(strip, color):
    amp = sa.getSoundPWM()
    if amp > 50:
        for i in range(strip.numPixels()):
        	strip.setPixelColor(i, color)
        strip.show()
        time.sleep(5 / 1000.0)
        for i in range(strip.numPixels()):
        	strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()


def runningLights(strip, color):
    global AKT_MODUS
    global RL_CARS
    global FLG_CHANGE_COLOR
    global FLG_CHANGE_EFFECT

    if AKT_MODUS != "RL":
        anz_cars = random.randint(1, 10)
        car_length = random.randint(2, 10)
        car_space = random.randint(3, 20)

        RL_CARS = []
        pos_offset = 0
        for i in range(anz_cars):
        	pos = []
        	for x in range(car_length):
        		pos.append(pos_offset)
        		pos_offset -= 1
        	RL_CARS.append(pos)
        	pos_offset-= car_space

    for x in range(strip.numPixels()):
        strip.setPixelColor(x, Color(0, 0, 0))

    for i in RL_CARS:
        for pos in i:
            strip.setPixelColor(pos, color)
            if pos + 1 >= strip.numPixels():
                RL_CARS[RL_CARS.index(i)][i.index(pos)] = 0
            else:
                RL_CARS[RL_CARS.index(i)][i.index(pos)] += 1

        if RL_CARS[0][0] == 133:
            FLG_CHANGE_EFFECT = 1


    strip.show()
    AKT_MODUS = "RL"
    FLG_CHANGE_COLOR = 1

def initializeTetris(strip, color):
    global TET_QUEUE_POS
    global TET_QUEUE_NEG
    global TET_LAUFNUMMER
    global FLG_CHANGE_COLOR
    global AKT_MODUS
    global TET_RICHTUNG
    global FLG_CHANGE_EFFECT

    if AKT_MODUS != "IT":
        TET_QUEUE_POS = 0
        TET_QUEUE_NEG = strip.numPixels() - 1
        TET_LAUFNUMMER = strip.numPixels() - 1

    strip.setPixelColor(TET_LAUFNUMMER, color)

    if TET_RICHTUNG == 1:
        strip.setPixelColor(TET_LAUFNUMMER + 1, Color(0, 0, 0))
    else:
        strip.setPixelColor(TET_LAUFNUMMER - 1, Color(0, 0, 0))
    strip.show()


    if TET_RICHTUNG == 1:
        if TET_LAUFNUMMER <= TET_QUEUE_POS:
            TET_LAUFNUMMER = TET_QUEUE_NEG
            TET_QUEUE_POS += 1
            FLG_CHANGE_COLOR = 1
            TET_RICHTUNG = random.randint(0, 1)
            if TET_RICHTUNG == 1:
                TET_LAUFNUMMER = TET_QUEUE_NEG - 1
            else:
                TET_LAUFNUMMER = TET_QUEUE_POS + 1
        else:
            TET_LAUFNUMMER -= 1
    else:
        if TET_LAUFNUMMER >= TET_QUEUE_NEG:
            TET_LAUFNUMMER = TET_QUEUE_POS
            TET_QUEUE_NEG -= 1
            FLG_CHANGE_COLOR = 1
            TET_RICHTUNG = random.randint(0, 1)
            if TET_RICHTUNG == 1:
                TET_LAUFNUMMER = TET_QUEUE_NEG - 1
            else:
                TET_LAUFNUMMER = TET_QUEUE_POS + 1
        else:
            TET_LAUFNUMMER += 1

    if TET_QUEUE_POS == TET_QUEUE_NEG:
        TET_QUEUE_POS = 0
        TET_QUEUE_NEG = strip.numPixels() - 1
        FLG_CHANGE_EFFECT = 1

    AKT_MODUS = "IT"

def light(strip, color):
    global AKT_MODUS
    global FLG_CHANGE_COLOR
    global FLG_CHANGE_EFFECT

    FLG_CHANGE_COLOR = 1
    FLG_CHANGE_EFFECT = 1

    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
    AKT_MODUS = "LI"


def chrystal(strip, color):
    global CH_TWINKLE
    global AKT_MODUS
    global FLG_CHANGE_COLOR
    global FLG_CHANGE_EFFECT

    if AKT_MODUS != "CH":
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))

    if len(CH_TWINKLE) == strip.numPixels():
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
        CH_TWINKLE = []
        FLG_CHANGE_EFFECT = 1

    twinkle = random.randint(0, strip.numPixels() - 1)

    if twinkle not in CH_TWINKLE:
        CH_TWINKLE.append(twinkle)
        strip.setPixelColor(twinkle, color)
    else:
        time.sleep(5 / 1000.0)
        chrystal(strip, color)


    strip.show()
    FLG_CHANGE_COLOR = 1
    AKT_MODUS = "CH"


def runningCircle(strip, color):
    global AKT_MODUS
    global FLG_CHANGE_COLOR
    global FLG_CHANGE_EFFECT
    global RC_LIST
    global RC_OFFSET_POS
    global RC_OFFSET_NEG
    global RC_RICHTUNG

    if AKT_MODUS != "RC":
        #Position ersten Pixels bestimmen
        firstPixel = random.randint(0, strip.numPixels() - 1)
        #RC_LIST = Liste schwarzer Pixel
        RC_LIST = []
        RC_LIST.append(firstPixel)

        #Display Liste
        for i in range(strip.numPixel()):
            if i not in RC_LIST:
                strip.setPixelColor(i, color)
            else:
                strip.setPixelColor(i, Color(0, 0, 0))

    AKT_MODUS = "RC"
    FLG_CHANGE_COLOR = 1


def readConfig():
    filepath = "/var/www/html/config.json"
    if os.path.isfile(filepath):
	       data = json.load(open(filepath))
	       return data

def randomizeEffectCounter():
    global EFFECT_COUNTER
    EFFECT_COUNTER = random.randint(2, 10)


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    opt_parse()
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)

    # Intialize the library (must be called once before other functions).
    strip.begin()
    initialize(strip, Color(255, 255, 255))

    effects = [initializeTetris, runningLights, chrystal, rainbow, runningCircle]
    music_effects = [equalizer, strobe]

    rainbow_counter = 0
    EFFECT_COUNTER = 1

    config = readConfig()
    if config["music_switch"] == True:
        randint = random.randint(0, len(music_effects) - 1)
    else:
        randint = random.randint(0, len(effects) - 1)

    while True:
        config = readConfig()
        if config["color_switch"] == True:
            color = wheel(rainbow_counter)
        else:
            brightness = config["range_brightness"] / 100.0
            color = Color(int(config["color_picker"]["r"] * brightness), int(config["color_picker"]["g"] * brightness), int(config["color_picker"]["b"] * brightness))

        if config["light_switch"] == True:
            light(strip, color)
            time.sleep(config["range_delay"] / 1000.0)
        elif config["music_switch"] == True:
            if EFFECT_COUNTER <= 1:
                randomizeEffectCounter()
                randint = random.randint(0, len(music_effects) - 1)
            music_effects[randint](strip, color)
        else:
            if EFFECT_COUNTER <= 1:
                randomizeEffectCounter()
                randint = random.randint(0, len(effects) - 1)
            #effects[randint](strip, color)

            effects[4](strip, color)
            time.sleep(config["range_delay"] / 1000.0)


        if FLG_CHANGE_COLOR == 1:
            if rainbow_counter >= 255:
                rainbow_counter = 0
            else:
                rainbow_counter += 1
            FLG_CHANGE_COLOR = 0

        #nach x-Aufrufen anderer Effekt
        if FLG_CHANGE_EFFECT == 1:
            EFFECT_COUNTER -= 1
            FLG_CHANGE_EFFECT = 0
