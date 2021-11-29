import time
from configargparse import ArgParser
import RPi.GPIO as GPIO

from azureKinectMKVRecorder import Recorder


if __name__ == '__main__':
	parser = ArgParser()
	parser.add('--fn', default='capture')
	parser.add('--gui', action='store_true')
	parser.add('--rec_config', help='relative path to rec_config.json file.', default='rec_config.json')
	parser.add('--out_dir', default=None)
	
	config = parser.parse_args()

	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(15, GPIO.IN)
	GPIO.setup(16, GPIO.IN)
	
	try:
		isRecording = False
		recorder = Recorder(config.gui, config.rec_config)

		pin15 = GPIO.input(15)
		pin16 = GPIO.input(16)

		print('Waiting for DO signal to start recording...')
		while True:
			curPin15 = GPIO.input(15)
			curPin16 = GPIO.input(16)

			if isRecording:
				# if pin15 0->1 | DO 1->0 (end recording)
				if not pin15 and curPin15:
					recorder.end()
					isRecording = False
					print('---------------')

				# if pin15=0 | DO 1 && pin16 1->0 (capture frame)
				if not curPin15 and (pin16 and not curPin16):
					recorder.recordFrame()
			else:
				# if pin15 1->0 | DO 0->1 (start recording)
				if pin15 and not curPin15:
					fn = config.fn + '_%d' % round(time.time())
					recorder.start(fn)
					isRecording = True

			pin15 = curPin15
			pin16 = curPin16

			time.sleep(.1)

	except KeyboardInterrupt:
		GPIO.cleanup()
		print('\nKeyboard Interrupt.')
	except:
		GPIO.cleanup()