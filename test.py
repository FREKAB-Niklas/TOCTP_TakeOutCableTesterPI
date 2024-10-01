import RPi.GPIO as GPIO
import time

ENCODER_PIN_A = 17

def callback(channel):
    print("Edge detected on pin", channel)

GPIO.setmode(GPIO.BCM)
GPIO.setup(ENCODER_PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Print the current state of the pin
print(f"Pin {ENCODER_PIN_A} state: {GPIO.input(ENCODER_PIN_A)}")

# Adding edge detection with debounce
GPIO.add_event_detect(ENCODER_PIN_A, GPIO.RISING, callback=callback, bouncetime=200)

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    GPIO.cleanup()
