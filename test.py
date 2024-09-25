import RPi.GPIO as GPIO

PIN=17

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)

print("GPIO setup successful.")
GPIO.cleanup()
