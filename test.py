import RPi.GPIO as GPIO

PIN=5

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)

print("GPIO setup successful.")
GPIO.cleanup()
