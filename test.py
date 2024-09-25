import RPi.GPIO as GPIO
import time

# Set the GPIO mode to BCM (Broadcom SOC channel numbers)
GPIO.setmode(GPIO.BCM)

# GPIO pins to test (you can test any pins you prefer)
test_pins = [17, 27, 22]

# Setup the GPIO pins as output (no physical device is required)
for pin in test_pins:
    GPIO.setup(pin, GPIO.OUT)
    print(f"Pin {pin} set up as OUTPUT.")

# Toggle each pin ON (HIGH) and OFF (LOW)
for pin in test_pins:
    GPIO.output(pin, GPIO.HIGH)
    print(f"Pin {pin} set to HIGH (ON).")
    time.sleep(1)
    
    GPIO.output(pin, GPIO.LOW)
    print(f"Pin {pin} set to LOW (OFF).")
    time.sleep(1)

# Cleanup the GPIO settings after the test
GPIO.cleanup()
print("GPIO cleanup complete.")
