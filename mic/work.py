# NeoPixel library strandtest example
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
import killswitch as ks

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
RC_negOffset = 0
RC_posOffset = 0
RC_posSkip = 0
RC_negSkip = 0
RC_flanke = 0
RC_fMultiplikator = 2

#Equalizer Config
EQ_PARTS = 0
EQ_LIST = []
HIST_AMP = 0
EQ_FREQ_MIN = 0
EQ_FREQ_MAX = 175

#SoundPulse config
SP_LIST =  []
SP_OFFSET = 0
SP_COLOR = Color(0, 0, 0)
SP_FREQ_MIN = 0
SP_FREQ_MAX = 350

#Strobe config
ST_FREQ_MIN = 0
ST_FREQ_MAX = 300

#theatreChase config
TC_POS = 0
TC_RICHTUNG = 0

#Debug config
DB_POS = 0

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

def equalizer(strip, color):
    global HIST_AMP
    global POS_OFFSET
    global AKT_MODUS
    global EQ_PARTS
    global EQ_LISTE
    global FLG_CHANGE_COLOR
    global FLG_CHANGE_EFFECT
    global EQ_FREQ_MIN
    global EQ_FREQ_MAX

    numPixels = strip.numPixels()

    if AKT_MODUS != "EQ":
        #Anzahl Teile ermitteln
        EQ_PARTS = random.randint(4, 8)
        EQ_LISTE = []
        #Start Offset
        randint = random.randint(0, numPixels - 1)

        #Start Offset in EQ_LISTE
        EQ_LISTE.append(randint)

        #Pixel auf Parts aufteilen
        anzahl = float(numPixels) / EQ_PARTS
        rest = numPixels - int(anzahl) * EQ_PARTS

        #Parts in Liste sichern
        for i in range(EQ_PARTS - 1):
            offset = EQ_LISTE[len(EQ_LISTE) - 1]
            nOffset = offset + int(anzahl)
            #wenn Offset > numPixels, dann aufteilen
            if nOffset > numPixels:
                nOffset = nOffset - numPixels
            EQ_LISTE.append(nOffset)

        reversedList = EQ_LISTE[::-1]

        #restliche Pixel platzieren
        reversedList = EQ_LISTE[::-1]
        c = 1
        for i in reversedList:
            index = EQ_LISTE.index(i)
            EQ_LISTE[index] = i + 1
            if c >= rest:
                break
            c += 1

    #Amplitude empfangen
    amp = sa.getSoundPWM(EQ_FREQ_MIN, EQ_FREQ_MAX)

    if amp > HIST_AMP:
        HIST_AMP = amp
        FLG_CHANGE_EFFECT = 1
    else:
        HIST_AMP -= int(HIST_AMP * 0.1)

    #Alles schwarz
    for i in range(numPixels):
        strip.setPixelColor(i, Color(0, 0, 0))

    #einzelne Parts durchlaufen da unterschiedlich lang
    for x in EQ_LISTE:
        index = EQ_LISTE.index(x)
        nIndex = index + 1
        #wenn letzter Index dann bis index 0
        if nIndex > len(EQ_LISTE) - 1:
            nIndex = 0

        c = EQ_LISTE[index]
        anzahlPixel = 1
        while True:
            #wenn c am naechsten Index Stop
            if c == EQ_LISTE[nIndex] - 1:
                break
            c += 1
            #wenn c > numPixels dann 0
            if c >= numPixels:
                c = 0
            anzahlPixel += 1

        #anzahlPixel je Amplitude
        auslenkung = int(anzahlPixel * HIST_AMP / 100)

        #Auslenkung anzeigen
        c = 1
        while c <= auslenkung:
            pixelIndex = EQ_LISTE[index] + c
            #wenn pixelIndex > numPixels bei 0 starten
            if pixelIndex > numPixels - 1:
                pixelIndex = pixelIndex - numPixels
            strip.setPixelColor(pixelIndex, color)
            c += 1

    strip.show()

    AKT_MODUS = "EQ"
    FLG_CHANGE_COLOR = 1


def strobe(strip, color):
    global AKT_MODUS
    global FLG_CHANGE_EFFECT
    global ST_FREQ_MIN
    global ST_FREQ_MAX

    amp = sa.getSoundPWM(ST_FREQ_MIN, ST_FREQ_MAX)

    if amp > 10:
        for i in range(strip.numPixels()):
        	strip.setPixelColor(i, Color(255, 255, 255))
        strip.show()
        time.sleep(5 / 1000.0)
        for i in range(strip.numPixels()):
        	strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()

        FLG_CHANGE_EFFECT = 1

    AKT_MODUS = "ST"

    time.sleep(50 / 1000.0)




def runningLights(strip, color):
    global AKT_MODUS, RL_CARS, FLG_CHANGE_COLOR, FLG_CHANGE_EFFECT

    if AKT_MODUS != "RL":
        anz_cars = random.randint(1, 10)
        RL_CARS = []
        pos_offset = 0
        for i in range(anz_cars):
            car_space = random.randint(3, 20)
            car_length = random.randint(2, 10)
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
            if pos >= 0 and pos < strip.numPixels():
                strip.setPixelColor(pos, color)
            if pos + 1 >= strip.numPixels():
                RL_CARS[RL_CARS.index(i)][i.index(pos)] = 0
            else:
                RL_CARS[RL_CARS.index(i)][i.index(pos)] += 1

    if RL_CARS[0][0] == strip.numPixels() - 1:
        FLG_CHANGE_EFFECT = 1

    strip.show()
    AKT_MODUS = "RL"
    FLG_CHANGE_COLOR = 1

def resetTetris():
    global TET_QUEUE_POS, TET_QUEUE_NEG, TET_LAUFNUMMER, TET_RICHTUNG
    numPixels = strip.numPixels()

    #Richtung 0 = auf linken Stapel, 1 auf rechten
    TET_RICHTUNG = random.randint(0, 1)

    if TET_RICHTUNG == 0:
        TET_LAUFNUMMER = TET_QUEUE_NEG - 1
    else:
        TET_LAUFNUMMER = TET_QUEUE_POS + 1


def initializeTetris(strip, color):
    global TET_QUEUE_POS, TET_QUEUE_NEG, TET_LAUFNUMMER, FLG_CHANGE_COLOR, AKT_MODUS, TET_RICHTUNG, FLG_CHANGE_EFFECT, EFFECT_COUNTER

    #Effekt nur einmal anzeigen
    EFFECT_COUNTER = 2

    numPixels = strip.numPixels()

    if AKT_MODUS != "IT":
        TET_QUEUE_POS = -1
        TET_QUEUE_NEG = numPixels - 1
        resetTetris()


    #Darstellung zwischen queu
    i = TET_QUEUE_POS + 1

    while i < TET_QUEUE_NEG:
        strip.setPixelColor(i, Color(0, 0, 0))
        i += 1

    #Laufnummer darstellen
    strip.setPixelColor(TET_LAUFNUMMER, color)

    strip.show()

    #Laufnummer verschieben
    if TET_RICHTUNG == 0:
        TET_LAUFNUMMER -= 1
    else:
        TET_LAUFNUMMER += 1

    #wenn Laufnummer Stapel erreicht
    if TET_LAUFNUMMER <= TET_QUEUE_POS:
        TET_QUEUE_POS += 1
        FLG_CHANGE_COLOR = 1
        resetTetris()

    if TET_LAUFNUMMER >= TET_QUEUE_NEG:
        TET_QUEUE_NEG -= 1
        FLG_CHANGE_COLOR = 1
        resetTetris()

    #Wenn beide Stapel erreicht - Reset
    if TET_QUEUE_POS >= TET_QUEUE_NEG:
        TET_QUEUE_POS = 0
        TET_QUEUE_NEG = numPixels - 1
        resetTetris()
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
        #time.sleep(5 / 1000.0)
        chrystal(strip, color)


    strip.show()
    FLG_CHANGE_COLOR = 1
    AKT_MODUS = "CH"


def runningCircle(strip, color):
    global AKT_MODUS
    global FLG_CHANGE_COLOR
    global FLG_CHANGE_EFFECT
    global RC_LIST
    global RC_negOffset
    global RC_posOffset
    global RC_flanke
    global RC_negSkip
    global RC_posSkip
    global RC_fMultiplikator

    #Start Operation
    if AKT_MODUS != "RC":
        #Position ersten Pixels bestimmen
        RC_posOffset = RC_negOffset = firstPixel = random.randint(0, strip.numPixels() - 1)
        #RC_LIST = Liste schwarzer Pixel
        RC_LIST = []
        RC_LIST.append(firstPixel)

        #eine Flanke schneller als andere
        RC_flanke = random.randint(0, 1)

        #Display Liste
        for i in range(strip.numPixels()):
            if i not in RC_LIST:
                strip.setPixelColor(i, color)
            else:
                strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()

    #laufende Operation

    #wenn Liste komplett Flanke aussuchen
    if len(RC_LIST) == strip.numPixels():
        RC_flanke = random.randint(0, 1)
        #Flanke Multiplikator
        RC_fMultiplikator = random.randint(1, 10)

        FLG_CHANGE_EFFECT = 1

    #Flanke Skip Steuerung
    if RC_flanke == 0:
        if RC_negSkip >= RC_fMultiplikator - 1:
            RC_negSkip = 0
        else:
            RC_negSkip += 1
        RC_posSkip = 0
    elif RC_flanke == 1:
        if RC_posSkip >= RC_fMultiplikator - 1:
            RC_posSkip = 0
        else:
            RC_posSkip += 1
        RC_negSkip = 0


    if RC_negSkip == 0:
        #negativer Part
        #neg Offset dekrementieren
        RC_negOffset -= 1
        #wenn Offset < 0 oder > 133 dann Position wechseln
        if RC_negOffset < 0:
            RC_negOffset = strip.numPixels() - 1

        #wenn Offset bereits in Liste -> Element aus Liste entfernen
        if RC_negOffset in RC_LIST:
            del RC_LIST[RC_LIST.index(RC_negOffset)]
        else:
            RC_LIST.insert(0, RC_negOffset)


    if RC_posSkip == 0:
        #positiver Part
        #pos Offset inkrementieren
        RC_posOffset += 1
        #wenn Offset < 0 oder > 133 dann Position wechseln
        if RC_posOffset > strip.numPixels() - 1:
            RC_posOffset = 0

        #wenn Offset bereits in Liste -> Element aus Liste entfernen
        if RC_posOffset in RC_LIST:
            del RC_LIST[RC_LIST.index(RC_posOffset)]
        else:
            RC_LIST.append(RC_posOffset)


    #Display Liste
    for i in range(strip.numPixels()):
        if i not in RC_LIST:
            strip.setPixelColor(i, color)
        else:
            strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

    AKT_MODUS = "RC"
    FLG_CHANGE_COLOR = 1

def SoundPulse(strip, color):
    global AKT_MODUS
    global SP_LIST
    global SP_OFFSET
    global FLG_CHANGE_COLOR
    global FLG_CHANGE_EFFECT
    global SP_FREQ_MIN
    global SP_FREQ_MAX

    #Farbwechsel bei amp limit
    global SP_COLOR

    numPixels = strip.numPixels()

    #Listenlaenge halbe Strecke
    listLength = int(numPixels / 2)

    if AKT_MODUS != "SP":
        #Start Position ermitteln
        SP_OFFSET = startPos = random.randint(0, numPixels - 1)
        SP_LIST = []
        SP_COLOR = color
        SP_LIST.append(SP_COLOR)

        for i in range(numPixels):
            strip.setPixelColor(i, Color(0, 0, 0))

    #wenn Amplitude > x, neue Farbe
    amp = sa.getSoundPWM(SP_FREQ_MIN, SP_FREQ_MAX)
    if amp > 40:
        SP_COLOR = wheel(random.randint(0, 255))
        FLG_CHANGE_EFFECT = 1


    #Listenelement 1 verschieben
    SP_LIST.insert(0, SP_COLOR)

    #wenn Liste > halbe Strecke, letztes Element raus
    if len(SP_LIST) > listLength:
        del SP_LIST[len(SP_LIST) - 1]

    #SP_LIST halb darstellen, Teil 1 positiv
    c = SP_OFFSET
    i = 0
    while i < listLength and i < len(SP_LIST):
        strip.setPixelColor(c, SP_LIST[i])
        i += 1
        c += 1
        if c >= numPixels -1:
            c = 0

    #SP_LIST darstellen, Teil 2
    c = SP_OFFSET - 1
    if c < 0:
        c = numPixels - 1
    i = 0 #Listenindex

    while i < listLength and i < len(SP_LIST):
        strip.setPixelColor(c, SP_LIST[i])
        i += 1
        c -= 1
        if c < 0:
            c = numPixels - 1

    strip.show()

    FLG_CHANGE_COLOR = 1
    AKT_MODUS = "SP"

def theatreChase(strip, color):
    global FLG_CHANGE_COLOR, FLG_CHANGE_EFFECT, AKT_MODUS, TC_POS, TC_RICHTUNG

    numPixels = strip.numPixels();

    if AKT_MODUS != "TC":
        TC_RICHTUNG = random.randint(0, 1)
        TC_POS = 0
        if TC_RICHTUNG == 1:
            TC_POS = numPixels - 1

    for x in range (numPixels):
        strip.setPixelColor(x, Color(0, 0, 0))

    #TC_POS aktuelle Position des ersten Pixels
    i = TC_POS
    while i < numPixels:
        strip.setPixelColor(i, Color(255, 0, 0))
        i += 3

    i = TC_POS
    while i >= 0:
        strip.setPixelColor(i, Color(255, 0, 0))
        i -= 3

    strip.show()

    if TC_RICHTUNG == 0:
        TC_POS += 1
        if TC_POS > numPixels:
            TC_POS = 0
            FLG_CHANGE_EFFECT = 1
    else:
        TC_POS -= 1
        if TC_POS < 0:
            TC_POS = numPixels - 1
            FLG_CHANGE_EFFECT = 1

    AKT_MODUS = "TC"
    FLG_CHANGE_COLOR = 1


def debug(strip, color):
    global FLG_CHANGE_COLOR, FLG_CHANGE_EFFECT, AKT_MODUS, DB_POS

    numPixels = strip.numPixels();

    if DB_POS >= numPixels:
        DB_POS = 0
        FLG_CHANGE_EFFECT = 1


    for x in range (numPixels):
        #print(x)
        strip.setPixelColor(x, Color(0, 0, 0))


    for x in range(DB_POS):
        strip.setPixelColor(x, color)

    DB_POS += 1
    strip.show()
    AKT_MODUS = "TC"
    FLG_CHANGE_COLOR = 1




def readConfig():
    filepath = "/var/www/html/config.json"
    if os.path.isfile(filepath):
        try:
	       data = json.load(open(filepath))
	       return data
        except:
           print("Error reading JSON")

def randomizeEffectCounter(start, end):
    global EFFECT_COUNTER
    EFFECT_COUNTER = random.randint(start, end)


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    opt_parse()
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)

    # Intialize the library (must be called once before other functions).
    strip.begin()
    #initialize(strip, Color(255, 255, 255))

    effects = [initializeTetris, runningLights, chrystal, rainbow, runningCircle, theatreChase, debug]
    effectsNames = ["initializeTetris", "runningLights", "chrystal", "rainbow", "runningCircle", "theatreChase", "debug"]
    #effects = [chrystal, rainbow, runningCircle, theatreChase]

    music_effects = [equalizer, strobe, SoundPulse]
    #music_effects = [equalizer, SoundPulse]
    music_effectsNames = ["equalizer", "strobe", "SoundPulse"]

    rainbow_counter = 0
    EFFECT_COUNTER = 1

    effectNum = effectNumMus = 0


    config = readConfig()

    if config["music_switch"] == True:
        effectNumMus = random.randint(0, len(music_effects) - 1)
    else:
        effectNum = random.randint(0, len(effects) - 1)

    while True:
        config = readConfig()

        ks.killswitch()

        if config["color_switch"] == True:
            color = wheel(rainbow_counter)
        else:
            color = Color(int(config["color_picker"]["r"]), int(config["color_picker"]["g"]), int(config["color_picker"]["b"]))
        if config["light_switch"] == True:
            light(strip, color)
            time.sleep(config["range_delay"] / 1000.0)
        elif config["singleeffect_switch"] == True:
            sEffect = config["select_effect"]
            if sEffect in effectsNames:
                effects[effectsNames.index(sEffect)](strip, color)
                time.sleep(config["range_delay"] / 1000.0)

            if sEffect in music_effectsNames:
                music_effects[music_effectsNames.index(sEffect)](strip, color)

        elif config["music_switch"] == True:
            if EFFECT_COUNTER <= 1:
                randomizeEffectCounter(100, 1000)
                effectNumMus = random.randint(0, len(music_effects) - 1)
                AKT_MODUS = ""
            music_effects[effectNumMus](strip, color)
        else:
            if EFFECT_COUNTER <= 1 or EFFECT_COUNTER > 30:
                randomizeEffectCounter(10, 30)
                effectNum = random.randint(0, len(effects) - 1)
                AKT_MODUS = ""
            effects[effectNum](strip, color)
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
