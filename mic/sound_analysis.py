import time
import spidata as sd
import numpy as np
import goertzel as go

running_max = []
running_max_size = 1000
freq_min = 20
freq_max = 175

def readSound(samples):
	buff = []
	t = []
	for i in range(samples):
		buff.append(sd.read_mcp3002(1))
		t.append(time.time() * 1000)
	return t, buff


def calc():
	global freq_min, freq_max
	window_size = 64
	t, sound = readSound(window_size)
	sample_rate = float(t[len(t) - 1] - t[0]) / 1000
	sample_rate = len(sound) / sample_rate
	freqs, results = go.goertzel(sound, sample_rate, (freq_min, freq_max))
	rarr = np.array(results)[:,2]
	max = np.amax(rarr)
	return max


def getSoundPWM():
	global running_max, running_max_size
	max = calc()
	if(len(running_max) >= running_max_size):
		temp = []
		for x in range(1, running_max_size):
			temp.append(running_max[x])
		running_max = temp
	running_max.append(max)

	max_running_max = np.amax(running_max)
	if max_running_max > 0:
		teil = int(max / max_running_max * 100)
	else:
		teil = 0
	return teil

if __name__ == '__main__':
	main()
