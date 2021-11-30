import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

GPIO.setup(15, GPIO.IN)
GPIO.setup(16, GPIO.IN)

x = GPIO.input(15)
print("Pin 15: %d" % x)

y = GPIO.input(16)
print("Pin 16: %d" % y)

GPIO.cleanup()