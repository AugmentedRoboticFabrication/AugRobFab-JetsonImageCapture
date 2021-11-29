import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(15, GPIO.IN)
GPIO.setup(16, GPIO.IN)

try:
	pin15 = GPIO.input(15)
	pin16 = GPIO.input(16)

	try:
		while True:
			curPin15 = GPIO.input(15)
			curPin16 = GPIO.input(16)

			print("Pin 15: %d" % curPin15)
			print("Pin 16: %d" % curPin16)

			# if pin15 1->0 | DO 0->1 (start recording)
			if pin15 and not curPin15:
				print('start recording')
			# if pin15 0->1 | DO 1->0 (end recording)
			if not pin15 and curPin15:
				print('end recording')
			# if pin15=0 | DO 1 && pin16 1->0 (capture frame)
			if not curPin15 and (pin16 and not curPin16):
				print('record frame')
			pin15 = curPin15
			pin16 = curPin16

			time.sleep(.1)
	except KeyboardInterrupt:
		GPIO.cleanup()
		print('\nForced quit.')
	except:
		GPIO.cleanup()