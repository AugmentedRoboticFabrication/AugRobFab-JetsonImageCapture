import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(15, GPIO.IN)
x = GPIO.input(15)
print("Pin 15: %b" %bool(x))

GPIO.cleanup()