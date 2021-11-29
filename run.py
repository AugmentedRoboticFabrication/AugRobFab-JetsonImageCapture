import os, datetime, keyboard
from configargparse import ArgParser
import RPi.GPIO as GPIO

from azureKinectMKVRecorder import Recorder


GPIO.cleanup()

if __name__ == '__main__':
	parser = ArgParser()
	parser.add('--fn', default='capture')
	parser.add('--no_gui', action='store_false')
	parser.add('--rec_config', help='relative path to rec_config.json file.', default='rec_config.json')
	parser.add('--out_dir', default=None)
	
	config = parser.parse_args()
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(15, GPIO.IN)
	GPIO.setup(16, GPIO.IN)
	
	recorder = None

	while True:
		startRecording = GPIO.input(15)

		if startRecording:
			fn = config.fn + '_%d' % round(time.time())
			recorder = Recorder(fn, config.no_gui, config.rec_config, config.out_dir)
		else:
			if recorder is not None:
				recorder.end()


		print("Pin 15: %d" % x)

		y = GPIO.input(16)
		print("Pin 16: %d" % y)


	recorder = Recorder(config.fn, config.no_gui, config.rec_config, config.out_dir)
	recorder.run()