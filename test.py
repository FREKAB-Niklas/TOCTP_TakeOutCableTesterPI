import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

print("GPIO setup successful.")
GPIO.cleanup()
