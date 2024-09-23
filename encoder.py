import RPi.GPIO as GPIO
import time

# Constants
PULSES_PER_REVOLUTION = 1000  # Check the encoder spec for correct value
WHEEL_CIRCUMFERENCE_MM = 157.08  # Set the circumference of the wheel in mm (50 mm diameter wheel)

# GPIO pin definitions
ENCODER_PIN_A = 17
ENCODER_PIN_B = 27

# Variables
last_encoder_a = GPIO.LOW
current_position = 0

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(ENCODER_PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENCODER_PIN_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def calculate_distance_mm(pulses):
    """Calculate distance traveled in mm based on encoder pulses"""
    distance_per_pulse = WHEEL_CIRCUMFERENCE_MM / PULSES_PER_REVOLUTION
    return pulses * distance_per_pulse

def encoder_callback(channel):
    global current_position
    encoder_b = GPIO.input(ENCODER_PIN_B)
    if encoder_b != GPIO.input(ENCODER_PIN_A):
        current_position += 1
    else:
        current_position -= 1

# Interrupt setup for rotary encoder
GPIO.add_event_detect(ENCODER_PIN_A, GPIO.BOTH, callback=encoder_callback)

try:
    while True:
        distance_mm = calculate_distance_mm(current_position)
        print(f"Distance traveled: {distance_mm:.2f} mm")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Measurement stopped.")

finally:
    GPIO.cleanup()
