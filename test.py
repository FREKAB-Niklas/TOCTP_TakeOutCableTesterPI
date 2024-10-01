import RPi.GPIO as GPIO
import time

ENCODER_PIN_A = 17

def callback(channel):
    print("Edge detected on pin", channel)

GPIO.setmode(GPIO.BCM)
GPIO.setup(ENCODER_PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(ENCODER_PIN_A, GPIO.BOTH, callback=callback)

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    GPIO.cleanup()

