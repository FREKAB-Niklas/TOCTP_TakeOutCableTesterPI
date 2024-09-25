import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

print("GPIO setup successful.")
GPIO.cleanup()
