import RPi.GPIO as GPIO
import time

ENCODER_PIN_A = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(ENCODER_PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        if GPIO.input(ENCODER_PIN_A) == GPIO.LOW:
            print("Pin is LOW")
        else:
            print("Pin is HIGH")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    GPIO.cleanup()
