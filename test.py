import RPi.GPIO as GPIO
import time

ENCODER_PIN_A = 17  # You can try a different pin like 22

def callback(channel):
    print("Edge detected on pin", channel)

GPIO.setmode(GPIO.BCM)
GPIO.setup(ENCODER_PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Adding edge detection with debounce
GPIO.add_event_detect(ENCODER_PIN_A, GPIO.RISING, callback=callback, bouncetime=200)

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    GPIO.cleanup()
